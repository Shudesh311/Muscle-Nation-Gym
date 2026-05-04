from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.contrib.auth import authenticate
from django.db import connection
from django.core.files.storage import FileSystemStorage
from datetime import datetime
from dateutil.relativedelta import relativedelta


def ensure_gym_fee_payment_columns():
    with connection.cursor() as cursor:
        columns = {column.name for column in connection.introspection.get_table_description(cursor, "gym_fees")}

        if "cash_amount" not in columns:
            cursor.execute("ALTER TABLE gym_fees ADD COLUMN cash_amount NUMERIC DEFAULT 0")

        if "gpay_amount" not in columns:
            cursor.execute("ALTER TABLE gym_fees ADD COLUMN gpay_amount NUMERIC DEFAULT 0")


@api_view(['POST'])
def login_view(request):
    username = request.data.get("username")
    password = request.data.get("password")

    if not username or not password:
        return Response({"error": "Missing username or password"}, status=400)

    user = authenticate(username=username, password=password)

    if user:
        return Response({"message": "Login success", "username": user.username}, status=200)

    return Response({"error": "Invalid credentials"}, status=401)


@api_view(['POST'])
def admin_create(request):
    username = request.data.get('username')
    password = request.data.get('password')

    if not username or not password:
        return Response({"error": "Missing fields"}, status=400)

    with connection.cursor() as cursor:
        cursor.execute(
            """
            INSERT INTO admin_users (username, password)
            VALUES (%s, %s)
            """,
            [username, password]
        )

    return Response({"message": "Admin created successfully"})
#########################################################################################
@api_view(['POST'])
def admin_login(request):
    username = request.data.get('username')
    password = request.data.get('password')

    if not username or not password:
        return Response({"error": "Missing fields"}, status=400)

    with connection.cursor() as cursor:
        cursor.execute(
            """
            SELECT id, username
            FROM admin_users
            WHERE username = %s AND password = %s
            """,
            [username, password]
        )
        admin = cursor.fetchone()

    if admin:
        return Response({
            "message": "Login successful",
            "username": admin[1]
        }, status=200)
    else:
        return Response({
            "error": "Invalid username or password"
        }, status=401)
##########################################################################################################
# CREATE NEW ADMISSION
# @api_view(['POST'])
# def create_admission(request):
#     admission_id = request.data.get('admission_id') or ""  # NOT NULL
#     name = request.data.get('name')
#     phone = request.data.get('phone')
#     admission_fees = request.data.get('admission_fees')
#     payment_method = request.data.get('payment_method')

#     if not name or not phone:
#         return Response(
#             {"error": "Name and Phone are required"},
#             status=400
#         )

#     try:
#         with connection.cursor() as cursor:
#             cursor.execute("""
#                 INSERT INTO new_admission
#                 (admission_id, name, phone, admission_fees, payment_method)
#                 VALUES (%s, %s, %s, %s, %s)
#             """, [
#                 admission_id,  # always string
#                 name,
#                 phone,
#                 admission_fees if admission_fees else None,
#                 payment_method if payment_method else None
#             ])

#         return Response({"message": "Admission added successfully"}, status=201)

#     except Exception as e:
#         return Response({"error": str(e)}, status=500)


# # GET ALL ADMISSIONS
# @api_view(['GET'])
# def list_admissions(request):
#     try:
#         with connection.cursor() as cursor:
#             cursor.execute("""
#                 SELECT id, admission_id, name, phone,
#                        admission_fees, payment_method, created_at
#                 FROM new_admission
#                 ORDER BY id DESC
#             """)
#             rows = cursor.fetchall()

#         data = []
#         for r in rows:
#             data.append({
#                 "id": r[0],
#                 "admission_id": r[1],
#                 "name": r[2],
#                 "phone": r[3],
#                 "admission_fees": r[4],
#                 "payment_method": r[5],
#                 "created_at": r[6],
#             })

#         return Response(data, status=200)

#     except Exception as e:
#         return Response({"error": str(e)}, status=500)
###########################################################
@api_view(['POST'])
def create_admission(request):
    admission_id = request.data.get('admission_id') or ""
    name = request.data.get('name')
    phone = request.data.get('phone')
    admission_fees = request.data.get('admission_fees')
    payment_method = request.data.get('payment_method')
    cash_amount = request.data.get('cash_amount')
    gpay_amount = request.data.get('gpay_amount')
    photo = request.FILES.get('photo')

    if not name or not phone:
        return Response({"error": "Name and Phone are required"}, status=400)

    photo_path = None
    if photo:
        fs = FileSystemStorage()
        filename = fs.save(photo.name, photo)
        photo_path = fs.url(filename)

    try:
        with connection.cursor() as cursor:
            cursor.execute("""
                INSERT INTO new_admission
                (admission_id, name, phone, admission_fees, payment_method, cash_amount, gpay_amount, photo)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, [
                admission_id,
                name,
                phone,
                admission_fees or None,
                payment_method or None,
                cash_amount or 0,
                gpay_amount or 0,
                photo_path
            ])

        return Response({"message": "Admission added"}, status=201)

    except Exception as e:
        return Response({"error": str(e)}, status=500)


@api_view(['GET'])
def list_admissions(request):
    try:
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT id, admission_id, name, phone,
                       admission_fees, payment_method, cash_amount, gpay_amount, photo, created_at
                FROM new_admission
                ORDER BY id DESC
            """)
            rows = cursor.fetchall()

        data = []
        for r in rows:
            data.append({
                "id": r[0],
                "admission_id": r[1],
                "name": r[2],
                "phone": r[3],
                "admission_fees": r[4],
                "payment_method": r[5],
                "cash_amount": r[6],
                "gpay_amount": r[7],
                "photo": r[8],
                "created_at": r[9],
            })

        return Response(data, status=200)

    except Exception as e:
        return Response({"error": str(e)}, status=500) 


@api_view(['DELETE'])
def delete_admission(request, admission_id):
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                DELETE FROM new_admission
                WHERE id = %s
                """,
                [admission_id]
            )

            if cursor.rowcount == 0:
                return Response({"error": "Admission not found"}, status=404)

        return Response({"message": "Admission deleted"}, status=200)

    except Exception as e:
        return Response({"error": str(e)}, status=500)
    
@api_view(['POST'])
def update_admission_photo(request, admission_id):
    photo = request.FILES.get('photo')
    if not photo:
        return Response({"error": "Photo required"}, status=400)

    fs = FileSystemStorage()
    filename = fs.save(photo.name, photo)
    photo_path = fs.url(filename)

    with connection.cursor() as cursor:
        cursor.execute("""
            UPDATE new_admission SET photo=%s WHERE id=%s
        """, [photo_path, admission_id])

    return Response({"message": "Photo updated"}, status=200)    
    #################################################################
    # ---------------- Add Gym Fee ----------------
@api_view(['POST'])
def add_gym_fee(request):
    admission_id = request.data.get("admission_id")  # VARCHAR
    workout_type = request.data.get("workout_type")
    duration = request.data.get("duration")
    payment_method = request.data.get("payment_method")
    cash_amount = request.data.get("cash_amount") or 0
    gpay_amount = request.data.get("gpay_amount") or 0
    start_date_str = request.data.get("start_date")
    end_date_str = request.data.get("end_date")

    if not admission_id:
        return Response({"error": "Admission ID required"}, status=400)

    if not duration:
        return Response({"error": "Duration required"}, status=400)

    duration = int(duration)

    # 🔹 Fetch user info using admission_id (VARCHAR)
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT admission_id, name, photo
            FROM new_admission
            WHERE admission_id = %s
        """, [admission_id])

        user = cursor.fetchone()

        if not user:
            return Response({"error": "User not found"}, status=404)

        admission_id, name, photo = user

    # 🔹 Calculate fees
    if workout_type == "strength":
        fees = 800 if duration == 1 else 1800
    else:  # cardio
        fees = 1200 if duration == 1 else 2700

    try:
        cash_amount = float(cash_amount)
        gpay_amount = float(gpay_amount)
    except (TypeError, ValueError):
        return Response({"error": "Invalid payment amount"}, status=400)

    if cash_amount < 0 or gpay_amount < 0:
        return Response({"error": "Payment amount cannot be negative"}, status=400)

    if cash_amount + gpay_amount != fees:
        return Response({"error": "Cash and GPay amounts must match the fees"}, status=400)

    # 🔹 Calculate dates
    start_date = datetime.strptime(start_date_str, "%Y-%m-%d").date()
    if end_date_str:
        end_date = datetime.strptime(end_date_str, "%Y-%m-%d").date()
    else:
        end_date = start_date + relativedelta(months=duration)

    # 🔹 Insert into gym_fees
    ensure_gym_fee_payment_columns()

    with connection.cursor() as cursor:
        cursor.execute("""
            INSERT INTO gym_fees
            (admission_id, name, photo, workout_type, duration_months, fees, start_date, end_date, payment_method, cash_amount, gpay_amount)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
        """, [
            admission_id,
            name,
            photo,
            workout_type,
            duration,
            fees,
            start_date,
            end_date,
            payment_method,
            cash_amount,
            gpay_amount
        ])

    return Response({"message": "Gym fee added successfully"}, status=201)

@api_view(['GET'])
def list_gym_fees(request):
    ensure_gym_fee_payment_columns()

    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT
                id,
                admission_id,
                name,
                photo,
                workout_type,
                duration_months,
                fees,
                start_date,
                end_date,
                payment_method,
                cash_amount,
                gpay_amount,
                created_at
            FROM gym_fees
            ORDER BY id DESC
        """)
        rows = cursor.fetchall()

    data = []
    for r in rows:
        data.append({
            "id": r[0],
            "admission_id": r[1],
            "name": r[2],
            "photo": r[3],
            "workout_type": r[4],
            "duration_months": r[5],
            "fees": r[6],
            "start_date": r[7],
            "end_date": r[8],
            "payment_method": r[9],
            "cash_amount": r[10],
            "gpay_amount": r[11],
            "created_at": r[12],
        })

    return Response(data, status=200)


@api_view(['GET'])
def search_admission(request):
    q = request.GET.get("q", "")
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT admission_id, name, photo
            FROM new_admission
            WHERE admission_id ILIKE %s OR name ILIKE %s
        """, [f"%{q}%", f"%{q}%"])
        rows = cursor.fetchall()

    return Response([
        {"admission_id": r[0], "name": r[1], "photo": r[2]}
        for r in rows
    ])
