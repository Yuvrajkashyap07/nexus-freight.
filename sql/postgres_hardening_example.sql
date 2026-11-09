-- EXAMPLE ONLY: reviewed production migration, not executed by the Streamlit demo.
-- The application must set the tenant context inside each transaction after authenticating
-- the user, e.g. SET LOCAL app.organization_id = '<authenticated-org-id>'.
-- Never accept organization_id from an untrusted client without validating membership.

ALTER TABLE customers ENABLE ROW LEVEL SECURITY;
ALTER TABLE carriers ENABLE ROW LEVEL SECURITY;
ALTER TABLE shipments ENABLE ROW LEVEL SECURITY;
ALTER TABLE quotes ENABLE ROW LEVEL SECURITY;
ALTER TABLE exceptions ENABLE ROW LEVEL SECURITY;
ALTER TABLE documents ENABLE ROW LEVEL SECURITY;
ALTER TABLE invoices ENABLE ROW LEVEL SECURITY;
ALTER TABLE audit_logs ENABLE ROW LEVEL SECURITY;

CREATE POLICY tenant_customers ON customers
  USING (organization_id = current_setting('app.organization_id', true))
  WITH CHECK (organization_id = current_setting('app.organization_id', true));
CREATE POLICY tenant_carriers ON carriers
  USING (organization_id = current_setting('app.organization_id', true))
  WITH CHECK (organization_id = current_setting('app.organization_id', true));
CREATE POLICY tenant_shipments ON shipments
  USING (organization_id = current_setting('app.organization_id', true))
  WITH CHECK (organization_id = current_setting('app.organization_id', true));
CREATE POLICY tenant_quotes ON quotes
  USING (organization_id = current_setting('app.organization_id', true))
  WITH CHECK (organization_id = current_setting('app.organization_id', true));
CREATE POLICY tenant_exceptions ON exceptions
  USING (organization_id = current_setting('app.organization_id', true))
  WITH CHECK (organization_id = current_setting('app.organization_id', true));
CREATE POLICY tenant_documents ON documents
  USING (organization_id = current_setting('app.organization_id', true))
  WITH CHECK (organization_id = current_setting('app.organization_id', true));
CREATE POLICY tenant_invoices ON invoices
  USING (organization_id = current_setting('app.organization_id', true))
  WITH CHECK (organization_id = current_setting('app.organization_id', true));
CREATE POLICY tenant_audit_logs ON audit_logs
  USING (organization_id = current_setting('app.organization_id', true))
  WITH CHECK (organization_id = current_setting('app.organization_id', true));

-- Restrict table permissions for runtime roles. Use separate migration/owner roles.
-- GRANT SELECT, INSERT, UPDATE, DELETE ON ... TO nexus_app;
-- GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO nexus_app;
