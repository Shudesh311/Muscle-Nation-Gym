from django.db import migrations


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.RunSQL(
            sql="""
                CREATE TABLE IF NOT EXISTS admin_users (
                    id SERIAL PRIMARY KEY,
                    username VARCHAR(150) NOT NULL UNIQUE,
                    password VARCHAR(255) NOT NULL,
                    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
                );

                CREATE TABLE IF NOT EXISTS new_admission (
                    id SERIAL PRIMARY KEY,
                    admission_id VARCHAR(100) NOT NULL,
                    name VARCHAR(255) NOT NULL,
                    phone VARCHAR(50) NOT NULL,
                    admission_fees NUMERIC DEFAULT 0,
                    payment_method VARCHAR(50),
                    cash_amount NUMERIC DEFAULT 0,
                    gpay_amount NUMERIC DEFAULT 0,
                    photo VARCHAR(500),
                    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
                );

                CREATE TABLE IF NOT EXISTS gym_fees (
                    id SERIAL PRIMARY KEY,
                    admission_id VARCHAR(100) NOT NULL,
                    name VARCHAR(255) NOT NULL,
                    photo VARCHAR(500),
                    workout_type VARCHAR(50),
                    duration_months INTEGER,
                    fees NUMERIC DEFAULT 0,
                    start_date DATE,
                    end_date DATE,
                    payment_method VARCHAR(50),
                    cash_amount NUMERIC DEFAULT 0,
                    gpay_amount NUMERIC DEFAULT 0,
                    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
                );
            """,
            reverse_sql="""
                DROP TABLE IF EXISTS gym_fees;
                DROP TABLE IF EXISTS new_admission;
                DROP TABLE IF EXISTS admin_users;
            """,
        )
    ]
