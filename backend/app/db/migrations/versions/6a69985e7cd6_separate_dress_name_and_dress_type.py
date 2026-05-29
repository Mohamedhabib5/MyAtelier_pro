"""separate dress name and dress type

Revision ID: 6a69985e7cd6
Revises: 95707d91cd1e
Create Date: 2026-05-29 18:59:00.000000
"""
from alembic import op
import sqlalchemy as sa
import uuid
from datetime import datetime, UTC

revision = '6a69985e7cd6'
down_revision = '95707d91cd1e'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # 1. Rename existing 'dress_type' column to 'legacy_dress_type' and make it nullable
    op.alter_column('dress_resources', 'dress_type', new_column_name='legacy_dress_type', nullable=True)

    # 2. Add 'name' and 'dress_type_id' columns as nullable initially
    op.add_column('dress_resources', sa.Column('name', sa.String(length=120), nullable=True))
    op.add_column('dress_resources', sa.Column('dress_type_id', sa.String(), nullable=True))

    # 3. Create foreign key constraint pointing to service_catalog_items
    op.create_foreign_key(
        'fk_dress_resources_dress_type_id_service_catalog_items',
        'dress_resources',
        'service_catalog_items',
        ['dress_type_id'],
        ['id'],
        ondelete='RESTRICT'
    )

    # 4. Migrate existing data
    connection = op.get_bind()
    
    # Select all active companies
    companies = connection.execute(sa.text("SELECT id FROM companies")).fetchall()
    
    for company in companies:
        company_id = company[0]
        
        # Get or create a dress department for this company
        dept = connection.execute(
            sa.text("SELECT id FROM departments WHERE company_id = :company_id AND is_dress_department = true LIMIT 1"),
            {"company_id": company_id}
        ).fetchone()
        
        if not dept:
            # If no dress department, find any active department or create one
            dept = connection.execute(
                sa.text("SELECT id FROM departments WHERE company_id = :company_id LIMIT 1"),
                {"company_id": company_id}
            ).fetchone()
            
            if not dept:
                # Create a default dress department
                dept_id = str(uuid.uuid4())
                connection.execute(
                    sa.text("""
                        INSERT INTO departments (id, company_id, code, name, is_active, is_dress_department, display_order, created_at, updated_at)
                        VALUES (:id, :company_id, :code, :name, true, true, 0, :now, :now)
                    """),
                    {
                        "id": dept_id,
                        "company_id": company_id,
                        "code": "DRESS",
                        "name": "الفساتين",
                        "now": datetime.now(UTC),
                    }
                )
                dept = (dept_id,)

        dept_id = dept[0]
        
        # Fetch all dresses for this company
        dresses = connection.execute(
            sa.text("SELECT id, code, legacy_dress_type FROM dress_resources WHERE company_id = :company_id"),
            {"company_id": company_id}
        ).fetchall()
        
        # Keep track of created services to avoid duplicates
        service_cache = {} # name -> id
        
        # Load existing services for this department
        existing_services = connection.execute(
            sa.text("SELECT id, name FROM service_catalog_items WHERE department_id = :dept_id"),
            {"dept_id": dept_id}
        ).fetchall()
        for s_id, s_name in existing_services:
            service_cache[s_name.strip()] = s_id

        for dress_id, code, legacy_type in dresses:
            type_str = (legacy_type or "عام").strip()
            
            # Find or create a ServiceCatalogItem for this dress type
            if type_str not in service_cache:
                s_id = str(uuid.uuid4())
                connection.execute(
                    sa.text("""
                        INSERT INTO service_catalog_items (
                            id, company_id, department_id, name, default_price, tax_rate_percent, duration_minutes, is_active, display_order, entity_version, created_at, updated_at
                        ) VALUES (
                            :id, :company_id, :dept_id, :name, 0.00, 0.00, 0, true, 0, 1, :now, :now
                        )
                    """),
                    {
                        "id": s_id,
                        "company_id": company_id,
                        "dept_id": dept_id,
                        "name": type_str,
                        "now": datetime.now(UTC),
                    }
                )
                service_cache[type_str] = s_id
            
            target_service_id = service_cache[type_str]
            dress_name = f"{type_str} {code}"
            
            # Update the dress record
            connection.execute(
                sa.text("""
                    UPDATE dress_resources 
                    SET name = :name, dress_type_id = :dress_type_id 
                    WHERE id = :id
                """),
                {
                    "name": dress_name,
                    "dress_type_id": target_service_id,
                    "id": dress_id
                }
            )

    # 5. Make the new columns non-nullable after populating them
    op.alter_column('dress_resources', 'name', nullable=False)
    op.alter_column('dress_resources', 'dress_type_id', nullable=False)


def downgrade() -> None:
    # 1. Drop foreign key constraint
    op.drop_constraint('fk_dress_resources_dress_type_id_service_catalog_items', 'dress_resources', type_='foreignkey')

    # 2. Drop the new columns
    op.drop_column('dress_resources', 'dress_type_id')
    op.drop_column('dress_resources', 'name')

    # 3. Rename 'legacy_dress_type' back to 'dress_type' and make it non-nullable
    op.alter_column('dress_resources', 'legacy_dress_type', new_column_name='dress_type', nullable=False)
