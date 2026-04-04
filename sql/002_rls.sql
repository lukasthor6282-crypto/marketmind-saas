ALTER TABLE usuarios ENABLE ROW LEVEL SECURITY;
ALTER TABLE analises ENABLE ROW LEVEL SECURITY;
ALTER TABLE produtos ENABLE ROW LEVEL SECURITY;
ALTER TABLE relatorios ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS usuarios_empresa_policy ON usuarios;
DROP POLICY IF EXISTS analises_empresa_policy ON analises;
DROP POLICY IF EXISTS produtos_empresa_policy ON produtos;
DROP POLICY IF EXISTS relatorios_empresa_policy ON relatorios;

CREATE POLICY usuarios_empresa_policy
ON usuarios
USING (empresa_id = current_setting('app.empresa_id', true)::INT);

CREATE POLICY analises_empresa_policy
ON analises
USING (empresa_id = current_setting('app.empresa_id', true)::INT)
WITH CHECK (empresa_id = current_setting('app.empresa_id', true)::INT);

CREATE POLICY produtos_empresa_policy
ON produtos
USING (empresa_id = current_setting('app.empresa_id', true)::INT)
WITH CHECK (empresa_id = current_setting('app.empresa_id', true)::INT);

CREATE POLICY relatorios_empresa_policy
ON relatorios
USING (empresa_id = current_setting('app.empresa_id', true)::INT)
WITH CHECK (empresa_id = current_setting('app.empresa_id', true)::INT);