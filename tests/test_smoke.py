import os
os.environ['WAREHOUSE_DB'] = ':memory:'

from fastapi.testclient import TestClient
from backend.app import app, init, db

# Initialize database schemas and seed data
init()

# Set client as a global but verify lifespan is entered
client=TestClient(app)
with client:
    pass

# Authenticated headers helper for test_create_order_full_flow
manager_login = client.post('/api/login', json={'username': 'demo_manager', 'password': 'Manager@123'}).json()
m_headers = {"Authorization": f"Bearer {manager_login['token']}"}

def test_health():
    r=client.get('/api/health'); assert r.status_code==200; assert r.json()['status']=='ok'

def test_root_endpoints():
    # Verify index.html loads successfully
    r_root = client.get('/')
    assert r_root.status_code == 200
    assert "Smart Warehouse" in r_root.text

    # Verify openapi.json loads successfully
    r_openapi = client.get('/openapi.json')
    assert r_openapi.status_code == 200
    assert "paths" in r_openapi.json()

def test_multi_item_orders():
    r=client.get('/api/orders'); assert r.status_code==200
    assert any(len(o['items'])>=2 for o in r.json())

def test_inventory_states():
    r=client.get('/api/inventory'); assert r.status_code==200
    assert all('available' in x and 'reserved' in x and 'allocated' in x for x in r.json())

def test_dashboard():
    r=client.get('/api/dashboard'); assert r.status_code==200; assert 'kpis' in r.json()

def test_simulation():
    r=client.post('/api/simulate',json={'stock_change':50,'demand_change':20,'pickers_unavailable':1,'urgent_order':True,'supplier_delay':2}); assert r.status_code==200

def test_login_and_auth():
    r=client.post('/api/login', json={'username': 'manager', 'password': 'manager123'})
    assert r.status_code == 200
    token = r.json()['token']
    assert token is not None

def test_create_order_full_flow():
    # Priority, Allocation, Picking, Packing, QC, Dispatch workflow
    # 1. Create order
    payload = {
        "customer_id": 1,
        "deadline_hours": 12,
        "items": [
            {"product_id": 1, "quantity": 2},
            {"product_id": 2, "quantity": 1}
        ]
    }
    r = client.post('/api/orders', json=payload, headers=m_headers)
    assert r.status_code == 200
    oid = r.json()['id']
    
    # 2. Pick order
    pick_res = client.post(f'/api/orders/{oid}/pick', headers=m_headers)
    assert pick_res.status_code == 200
    assert 'route' in pick_res.json()
    
    # 3. Pack order
    pack_res = client.post(f'/api/orders/{oid}/pack', headers=m_headers)
    assert pack_res.status_code == 200
    
    # 4. Quality check
    qc_res = client.post(f'/api/orders/{oid}/qc', json={'action': 'PASS', 'reason': 'Verification passed'}, headers=m_headers)
    assert qc_res.status_code == 200
    
    # 5. Dispatch
    disp_res = client.post(f'/api/orders/{oid}/dispatch', headers=m_headers)
    assert disp_res.status_code == 200

def test_cancel_order_releases_inventory():
    payload = {
        "customer_id": 2,
        "deadline_hours": 24,
        "items": [{"product_id": 3, "quantity": 2}]
    }
    r = client.post('/api/orders', json=payload, headers=m_headers)
    oid = r.json()['id']
    
    # Cancel order
    cancel_res = client.post(f'/api/orders/{oid}/cancel', headers=m_headers)
    assert cancel_res.status_code == 200
    
    # Check order is cancelled
    orders = client.get('/api/orders').json()
    cancelled_order = next(o for o in orders if o['id'] == oid)
    assert cancelled_order['status'] == 'CANCELLED'

def test_misplaced_item_exception_creation():
    # Misplaced flow
    r = client.post('/api/inventory/1/mark-misplaced', json={'reason': 'Bin mismatch'})
    assert r.status_code == 200
    
    # Verify exception is logged
    exceptions = client.get('/api/exceptions').json()
    assert any(x['type'] == 'Misplaced item' for x in exceptions)

def test_business_rule_update():
    r = client.post('/api/business-rules/update', json={'name': 'critical_deadline_hours', 'value': 18})
    assert r.status_code == 200
    
    rules = client.get('/api/business-rules').json()
    target_rule = next(x for x in rules if x['name'] == 'critical_deadline_hours')
    assert target_rule['value'] == 18

def test_human_approvals_workflow():
    # Test getting current pending approvals
    r = client.get('/api/approvals')
    assert r.status_code == 200
    approvals = r.json()
    assert len(approvals) > 0
    target_id = approvals[0]['id']

    # Approve recommendation
    action_res = client.post(f'/api/approvals/{target_id}/action', json={'user': 'manager', 'action': 'APPROVED'})
    assert action_res.status_code == 200

    # Verify status changed in list
    updated = client.get('/api/approvals').json()
    assert next(x for x in updated if x['id'] == target_id)['status'] == 'APPROVED'

def test_workforce_reassignment():
    # Test worker workloads reassign
    r = client.post('/api/workers/reassign', json={'worker_id': 1, 'action_notes': 'Transferred to urgent picker task'})
    assert r.status_code == 200
    
    # Verify logged inside audit trail
    audits = client.get('/api/audit').json()
    assert any('Reassigned worker' in x['action'] for x in audits)

def test_user_registration_suite():
    # 1. Successful registration
    reg_data = {
        "fullname": "New Picker Worker",
        "username": "new_picker_operator",
        "email": "picker_op@warehouse.com",
        "password": "SecurePassword123",
        "confirm_password": "SecurePassword123",
        "role": "PICKER"
    }
    r = client.post('/api/register', json=reg_data)
    assert r.status_code == 200
    assert "Account created successfully" in r.json()['message']

    # 2. Duplicate username check
    r2 = client.post('/api/register', json=reg_data)
    assert r2.status_code == 400
    assert "Username already exists" in r2.json()['detail']

    # 3. Duplicate email check
    reg_data_dup_email = reg_data.copy()
    reg_data_dup_email["username"] = "another_unique_name"
    r3 = client.post('/api/register', json=reg_data_dup_email)
    assert r3.status_code == 400
    assert "Email already registered" in r3.json()['detail']

    # 4. Weak password check
    reg_data_weak_pass = reg_data.copy()
    reg_data_weak_pass["username"] = "another_unique_name2"
    reg_data_weak_pass["email"] = "unique2@warehouse.com"
    reg_data_weak_pass["password"] = "weak"
    reg_data_weak_pass["confirm_password"] = "weak"
    r4 = client.post('/api/register', json=reg_data_weak_pass)
    assert r4.status_code == 400
    assert "Password does not meet security requirements" in r4.json()['detail']

    # 5. Password mismatch check
    reg_data_mismatch = reg_data.copy()
    reg_data_mismatch["username"] = "another_unique_name3"
    reg_data_mismatch["email"] = "unique3@warehouse.com"
    reg_data_mismatch["password"] = "SecurePassword123"
    reg_data_mismatch["confirm_password"] = "MismatchedPass123"
    r5 = client.post('/api/register', json=reg_data_mismatch)
    assert r5.status_code == 400
    assert "Passwords do not match" in r5.json()['detail']

    # 6. Successful login with newly registered credentials
    login_res = client.post('/api/login', json={'username': 'new_picker_operator', 'password': 'SecurePassword123'})
    assert login_res.status_code == 200
    assert login_res.json()['role'] == 'PICKER'
    assert login_res.json()['fullname'] == 'New Picker Worker'

    # 7. Profile endpoint access with new user JWT
    token = login_res.json()['token']
    me_res = client.get('/api/users/me', headers={'Authorization': f'Bearer {token}'})
    assert me_res.status_code == 200
    assert me_res.json()['fullname'] == 'New Picker Worker'

def test_demo_accounts_exist_and_login():
    demos = [
        ('demo_picker', 'Picker@123', 'PICKER'),
        ('demo_packer', 'Packer@123', 'PACKING_STAFF'),
        ('demo_qc', 'QC@123', 'QC_STAFF'),
        ('demo_dispatch', 'Dispatch@123', 'DISPATCH_STAFF'),
        ('demo_manager', 'Manager@123', 'WAREHOUSE_MANAGER'),
    ]
    for username, password, expected_role in demos:
        r = client.post('/api/login', json={'username': username, 'password': password})
        assert r.status_code == 200, f"Failed login for {username}"
        assert r.json()['role'] == expected_role

def test_manual_order_creation_flows():
    # 1. Valid manual order entry
    payload = {
        "customer_name": "Test Customer Manual",
        "customer_contact": "test@manual.com",
        "priority": "CRITICAL",
        "items": [
            {"product_id": 1, "quantity": 5},
            {"product_id": 2, "quantity": 1}
        ]
    }
    r = client.post('/api/orders', json=payload)
    assert r.status_code == 200
    assert r.json()['id'] is not None

    # Verify order is saved and queries back containing customer name
    orders_list = client.get('/api/orders').json()
    created_ord = next(o for o in orders_list if o['id'] == r.json()['id'])
    assert created_ord['customer'] == 'Test Customer Manual'
    assert created_ord['priority'] == 'CRITICAL'

    # 2. Reject empty items
    payload_empty = {
        "customer_name": "No Items Customer",
        "priority": "NORMAL",
        "items": []
    }
    r_empty = client.post('/api/orders', json=payload_empty)
    assert r_empty.status_code == 400

    # 3. Reject invalid qty
    payload_invalid_qty = {
        "customer_name": "Bad Qty Customer",
        "priority": "NORMAL",
        "items": [{"product_id": 1, "quantity": -5}]
    }
    r_bad_qty = client.post('/api/orders', json=payload_invalid_qty)
    assert r_bad_qty.status_code == 400

def test_product_onboarding_and_lifecycle_suite():
    # Manager token
    manager_login = client.post('/api/login', json={'username': 'demo_manager', 'password': 'Manager@123'}).json()
    m_token = manager_login['token']
    headers = {"Authorization": f"Bearer {m_token}"}

    # Picker token (to test RBAC)
    picker_login = client.post('/api/login', json={'username': 'demo_picker', 'password': 'Picker@123'}).json()
    p_token = picker_login['token']
    p_headers = {"Authorization": f"Bearer {p_token}"}

    # 1. Reject unauthorized role product onboarding
    bad_rbac = client.post('/api/products', json={
        "name": "Bad RBAC Device", "sku": "BAD-111", "category": "Gadgets", "zone": "Z1", "location": "B1",
        "initial_stock": 10, "reorder_level": 5, "safety_stock": 2, "lead_time_days": 1, "unit_price": 5.0
    }, headers=p_headers)
    assert bad_rbac.status_code == 403

    # 2. Reject negative numbers
    neg_stock = client.post('/api/products', json={
        "name": "Bad Stock", "sku": "BAD-222", "category": "Gadgets", "zone": "Z1", "location": "B1",
        "initial_stock": -10, "reorder_level": 5, "safety_stock": 2, "lead_time_days": 1, "unit_price": 5.0
    }, headers=headers)
    assert neg_stock.status_code == 422

    neg_reorder = client.post('/api/products', json={
        "name": "Bad Reorder", "sku": "BAD-333", "category": "Gadgets", "zone": "Z1", "location": "B1",
        "initial_stock": 10, "reorder_level": -5, "safety_stock": 2, "lead_time_days": 1, "unit_price": 5.0
    }, headers=headers)
    assert neg_reorder.status_code == 422

    neg_price = client.post('/api/products', json={
        "name": "Bad Price", "sku": "BAD-444", "category": "Gadgets", "zone": "Z1", "location": "B1",
        "initial_stock": 10, "reorder_level": 5, "safety_stock": 2, "lead_time_days": 1, "unit_price": -5.0
    }, headers=headers)
    assert neg_price.status_code == 422

    # 3. Successful product onboarding
    payload = {
        "name": "Smart Scanner Pro",
        "sku": "SSP-1001",
        "category": "Warehouse Equipment",
        "description": "New generation warehouse scanner",
        "unit_price": 249.99,
        "supplier": "Demo Supplier",
        "zone": "ZONE-C",
        "location": "BIN-C-12",
        "initial_stock": 100,
        "reorder_level": 20,
        "safety_stock": 10,
        "lead_time_days": 5,
        "status": "ACTIVE"
    }
    r = client.post('/api/products', json=payload, headers=headers)
    assert r.status_code == 200
    pid = r.json()['id']
    assert pid is not None

    # 4. Reject duplicate SKU
    dup_sku = client.post('/api/products', json=payload, headers=headers)
    assert dup_sku.status_code == 400

    # 5. Verify product details are retrieved correctly
    det = client.get(f'/api/products/{pid}/details').json()
    assert det['name'] == 'Smart Scanner Pro'
    assert det['sku'] == 'SSP-1001'
    assert det['available'] == 100

    # 6. Verify product appears in inventory API
    inv = client.get('/api/inventory').json()
    item = next(x for x in inv if x['product_id'] == pid)
    assert item['sku'] == 'SSP-1001'
    assert item['available'] == 100
    assert item['state'] == 'HEALTHY'

    # 7. Edit product details
    edit_payload = {
        "name": "Smart Scanner Pro V2",
        "category": "Warehouse Equipment",
        "description": "Upgraded generation warehouse scanner",
        "unit_price": 279.99,
        "supplier": "Demo Supplier Ltd",
        "reorder_level": 15,
        "safety_stock": 8,
        "lead_time_days": 4,
        "zone": "ZONE-D",
        "location": "BIN-D-01",
        "status": "ACTIVE"
    }
    r_edit = client.post(f'/api/products/{pid}/update', json=edit_payload, headers=headers)
    assert r_edit.status_code == 200

    det_edited = client.get(f'/api/products/{pid}/details').json()
    assert det_edited['name'] == 'Smart Scanner Pro V2'
    assert det_edited['zone'] == 'ZONE-D'
    assert det_edited['unit_price'] == 279.99

    # 8. Deactivate product and verify it is INACTIVE
    deact_payload = edit_payload.copy()
    deact_payload['status'] = 'INACTIVE'
    r_deact = client.post(f'/api/products/{pid}/update', json=deact_payload, headers=headers)
    assert r_deact.status_code == 200

    det_deact = client.get(f'/api/products/{pid}/details').json()
    assert det_deact['status'] == 'INACTIVE'

def test_hackathon_winning_upgrade_suite():
    # Manager token
    manager_login = client.post('/api/login', json={'username': 'demo_manager', 'password': 'Manager@123'}).json()
    m_token = manager_login['token']
    headers = {"Authorization": f"Bearer {m_token}"}

    # 1. Reset demo scenario
    r_reset = client.post('/api/recovery-plans/reset-demo', json={})
    assert r_reset.status_code == 200

    # 2. Verify Control Tower operational health loads successfully
    ct = client.get('/api/control-tower').json()
    assert ct['health_score'] is not None
    assert ct['active_exceptions'] > 0

    # 3. Verify alerts feed loads
    alerts = client.get('/api/control-tower/alerts').json()
    assert len(alerts) > 0
    # There should be at least one Stock shortage alert from our recovery reset
    shortage_alert = next(a for a in alerts if "shortage" in a['problem'].lower() or "shortage" in a['reason'].lower())
    assert shortage_alert is not None

    # 4. Verify bottlenecks lists
    bottlenecks = client.get('/api/control-tower/bottlenecks').json()
    assert len(bottlenecks) > 0

    # 5. Verify SLA risks prediction outputs
    risks = client.get('/api/control-tower/sla-risks').json()
    assert len(risks) > 0
    recovery_risk = next(r for r in risks if r['order_no'] == 'ORD-DEMO-RECOVERY')
    assert recovery_risk['status'] == 'AT RISK'

    # 6. Retrieve recovery plans for the generated shortage exception
    ex_id = shortage_alert['id']
    plans = client.get(f'/api/recovery-plans/{ex_id}').json()
    assert len(plans) == 3
    plan_b = next(p for p in plans if p['name'] == 'PLAN B – REALLOCATION')
    assert plan_b['score'] == 90 # Recommended reallocation score

    # 7. Approve recovery plan B - Reallocation and verify successful outcome
    r_approve = client.post('/api/recovery-plans/2/approve', json={"exception_id": ex_id}, headers=headers)
    assert r_approve.status_code == 200
    assert "reallocated" in r_approve.json()['result'].lower()

    # 8. Non-manager role rejection check
    picker_login = client.post('/api/login', json={'username': 'demo_picker', 'password': 'Picker@123'}).json()
    p_token = picker_login['token']
    p_headers = {"Authorization": f"Bearer {p_token}"}
    r_approve_p = client.post('/api/recovery-plans/2/approve', json={"exception_id": ex_id}, headers=p_headers)
    assert r_approve_p.status_code == 403

    # 9. Verify decisions history listing contains the approved record
    decisions = client.get('/api/decisions').json()
    assert len(decisions) > 0
    exec_dec = next(d for d in decisions if d['exception_id'] == ex_id)
    assert exec_dec['status'] == 'EXECUTED'

def test_recommendation_pipeline_center():
    # Manager token
    manager_login = client.post('/api/login', json={'username': 'demo_manager', 'password': 'Manager@123'}).json()
    m_token = manager_login['token']
    headers = {"Authorization": f"Bearer {m_token}"}

    # Picker token
    picker_login = client.post('/api/login', json={'username': 'demo_picker', 'password': 'Picker@123'}).json()
    p_token = picker_login['token']
    p_headers = {"Authorization": f"Bearer {p_token}"}

    # 1. API retrieves generated recommendations
    recs = client.get('/api/approvals').json()
    assert len(recs) >= 4
    
    # Verify our seeded demo alerts exist
    reorder_rec = next(r for r in recs if r['title'] == 'LOW STOCK / REORDER')
    assert reorder_rec['priority'] == 'HIGH'
    assert reorder_rec['status'] == 'PENDING'

    # 2. Manager Approve action executes successfully
    r_approve = client.post(f"/api/approvals/{reorder_rec['id']}/action", json={
        "action": "APPROVED",
        "user": "demo_manager"
    }, headers=headers)
    assert r_approve.status_code == 200

    # Verify state updated in DB
    recs_updated = client.get('/api/approvals').json()
    reorder_rec_up = next(r for r in recs_updated if r['id'] == reorder_rec['id'])
    assert reorder_rec_up['status'] == 'APPROVED'
    assert reorder_rec_up['reviewed_by'] == 'demo_manager'

    # 3. Manager Reject action with reason executes successfully
    shortage_rec = next(r for r in recs if r['title'] == 'URGENT INVENTORY SHORTAGE')
    r_reject = client.post(f"/api/approvals/{shortage_rec['id']}/action", json={
        "action": "REJECTED",
        "user": "demo_manager",
        "reject_reason": "Alternative delivery options chosen"
    }, headers=headers)
    assert r_reject.status_code == 200

    # Verify status and reason persist
    recs_updated2 = client.get('/api/approvals').json()
    shortage_rec_up = next(r for r in recs_updated2 if r['id'] == shortage_rec['id'])
    assert shortage_rec_up['status'] == 'REJECTED'
    assert shortage_rec_up['reject_reason'] == 'Alternative delivery options chosen'

    # 4. Picker role access fails on approval updates (RBAC safety check)
    optimization_rec = next(r for r in recs if r['title'] == 'WORKFORCE OPTIMIZATION')
    r_bad_rbac = client.post(f"/api/approvals/{optimization_rec['id']}/action", json={
        "action": "APPROVED",
        "user": "demo_picker"
    }, headers=p_headers)
    assert r_bad_rbac.status_code == 403

def test_qc_and_dispatch_fulfillment_workflows():
    # 1. Login auth tokens
    qc_tok = client.post('/api/login', json={'username': 'demo_qc', 'password': 'QC@123'}).json()['token']
    qc_headers = {"Authorization": f"Bearer {qc_tok}"}

    disp_tok = client.post('/api/login', json={'username': 'demo_dispatch', 'password': 'Dispatch@123'}).json()['token']
    disp_headers = {"Authorization": f"Bearer {disp_tok}"}

    picker_tok = client.post('/api/login', json={'username': 'demo_picker', 'password': 'Picker@123'}).json()['token']
    picker_headers = {"Authorization": f"Bearer {picker_tok}"}

    orders = client.get('/api/orders').json()
    
    # 2. Verify seeded demo orders exist
    ord1 = next(o for o in orders if o['order_no'] == 'ORD-DEMO-001')
    ord2 = next(o for o in orders if o['order_no'] == 'ORD-DEMO-002')
    ord3 = next(o for o in orders if o['order_no'] == 'ORD-DEMO-003')
    ord4 = next(o for o in orders if o['order_no'] == 'ORD-DEMO-004')

    assert ord1['status'] == 'PENDING_QC'
    assert ord2['status'] == 'READY_FOR_DISPATCH'
    assert ord3['status'] == 'PICKING'
    assert ord4['status'] == 'PACKING'

    # 3. RBAC checks - Picker role should fail to approve QC
    r_bad_qc = client.post(f"/api/orders/{ord1['id']}/qc", json={"action": "PASS"}, headers=picker_headers)
    assert r_bad_qc.status_code == 403

    # 4. QC approval workflow execution
    r_ok_qc = client.post(f"/api/orders/{ord1['id']}/qc", json={"action": "PASS"}, headers=qc_headers)
    assert r_ok_qc.status_code == 200

    # Verify status changed in database
    orders_post_qc = client.get('/api/orders').json()
    ord1_updated = next(o for o in orders_post_qc if o['id'] == ord1['id'])
    assert ord1_updated['status'] == 'READY_FOR_DISPATCH'
    assert ord1_updated['qc_status'] == 'PASSED'

    # 5. Dispatch workflow execution
    # Verify Dispatch role can dispatch READY_FOR_DISPATCH orders
    r_ok_disp = client.post(f"/api/orders/{ord1['id']}/dispatch", headers=disp_headers)
    assert r_ok_disp.status_code == 200

    # Verify status is updated to COMPLETED / fulfilled
    orders_post_disp = client.get('/api/orders').json()
    ord1_dispatched = next(o for o in orders_post_disp if o['id'] == ord1['id'])
    assert ord1_dispatched['status'] == 'COMPLETED'
    assert ord1_dispatched['fulfillment_status'] == 'COMPLETED'

    # 6. QC rejection workflow execution
    # Seed a new order to test rejection flow
    payload_rej = {
        "customer_name": "Rejection Tech",
        "priority": "HIGH",
        "items": [{"product_id": 1, "quantity": 1}]
    }
    r_new_ord = client.post('/api/orders', json=payload_rej)
    assert r_new_ord.status_code == 200
    new_oid = r_new_ord.json()['id']

    # Advance state to PENDING_QC for testing
    c = db()
    c.execute('update orders set status="PENDING_QC", packing_status="COMPLETED" where id=?', (new_oid,))
    c.commit()

    # Reject QC flow
    r_reject = client.post(f"/api/orders/{new_oid}/qc", json={"action": "FAIL", "reason": "Packaging is torn"}, headers=qc_headers)
    assert r_reject.status_code == 200

    # Verify order state returns to PACKING
    orders_post_rej = client.get('/api/orders').json()
    ord_rej = next(o for o in orders_post_rej if o['id'] == new_oid)
    assert ord_rej['status'] == 'PACKING'
    assert ord_rej['packing_status'] == 'PENDING'
    assert ord_rej['qc_status'] == 'FAILED'

    # Verify audit logs update
    audits = client.get('/api/audit').json()
    assert any("QC check resolved: FAILED" in a['action'] for a in audits)

def test_analytics_charts_endpoint():
    # 1. API endpoint returns expected chart data metrics
    r = client.get('/api/analytics')
    assert r.status_code == 200
    data = r.json()
    assert 'orders' in data
    assert 'pending' in data
    assert 'completed' in data
    assert 'workers' in data
    assert 'fulfillment_rate' in data

def test_product_image_upload_and_retrieval():
    # Manager login
    manager_login = client.post('/api/login', json={'username': 'demo_manager', 'password': 'Manager@123'}).json()
    m_token = manager_login['token']
    headers = {"Authorization": f"Bearer {m_token}"}

    # Simulate product onboarding with file upload
    import io
    dummy_file = io.BytesIO(b"dummy image content")
    files = {"image": ("test_upload.jpg", dummy_file, "image/jpeg")}
    
    # Form data payload
    data = {
        "name": "Image Camera",
        "sku": "SKU-IMG-999",
        "category": "Electronics",
        "description": "Onboard test camera",
        "unit_price": "99.99",
        "supplier": "Cam Supplier",
        "zone": "ZONE-C",
        "location": "BIN-C-09",
        "initial_stock": "15",
        "reorder_level": "3",
        "safety_stock": "2",
        "lead_time_days": "2",
        "status": "ACTIVE"
    }

    response = client.post(
        '/api/products',
        data=data,
        files=files,
        headers=headers
    )
    assert response.status_code == 200
    res_data = response.json()
    pid = res_data['id']
    assert "/static/images/products/SKU-IMG-999_test_upload.jpg" in res_data['image_path']

    # Retrieve inventory and verify the image_path is returned
    inventory = client.get('/api/inventory').json()
    item = next(x for x in inventory if x['product_id'] == pid)
    assert "/static/images/products/SKU-IMG-999_test_upload.jpg" in item['image_path']




