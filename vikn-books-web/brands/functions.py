import psycopg2
from django.conf import settings
from django.db import connection
from django import db
import psycopg2
import django.conf as conf
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from django.core.management.commands import loaddata
from django.core.management import call_command
import re

database = "test"
user = "vikncodes"
password = "vikncodes123"
host = "localhost"
port = "5432"

def get_DBS():
    DB = {'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': database,
        'USER': user,
        'PASSWORD': password,
        'HOST': host,
        'PORT': '',
    },}
    try:
        connection = psycopg2.connect(
           database=database, 
           user = user, 
           password = password, 
           host = host, 
           port = port
        )


        cursor = connection.cursor()
        
        sql = "SELECT * FROM db_store" 
        # Print PostgreSQL version
        cursor.execute(sql)
        records = cursor.fetchall()

        for row in records:
            db_data = {
                'ENGINE': 'django.db.backends.postgresql_psycopg2',
                'NAME': row[2],
                'USER': row[7],
                'PASSWORD': row[8],
                'HOST': row[26],
                'PORT': row[27]
            }

            DB['default'+str(row[0])] = db_data
            # conf.settings.DATABASES['default'+str(row[0])] = db_data

        cursor.close()
        connection.close()

    except (Exception, psycopg2.Error) as error :
        print ("Error while connecting to PostgreSQL", error)

    DATABASES = DB

    return DATABASES


def createdb(companyname,address1,address2,address3,city,state,country,postalcode,telephone,mobile,email,website,currency,fractionalunit,vatnumber,gstnumber,tax1,tax2,tax3,customerid,):
    from users.models import DatabaseStore
    from brands.management.commands import process_db

    connection = None

    success = False

    # name = "jas12"
    username = "vikncodes"
    password = "vikncodes123"
    host = "localhost"
    port = "5432"
    migration_db = None

    companyname = companyname
    address1 = address1
    address2 = address2
    address3 = address3
    city = city
    state = state
    country = country
    postalcode = postalcode
    telephone = telephone
    mobile = mobile
    email = email
    website = website
    currency = currency
    fractionalunit = fractionalunit
    vatnumber = vatnumber
    gstnumber = gstnumber
    tax1 = tax1
    tax2 = tax2
    tax3 = tax3
    customerid = customerid

    
    # try:
    connection = psycopg2.connect(
       database=database, 
       user = user, 
       password = password, 
       host = host,
       port = port
    )


    cursor = connection.cursor()

    sql1 = "SELECT id FROM db_store ORDER BY id DESC LIMIT 1";
    cursor.execute(sql1)
    db_id = cursor.fetchone()

    DatabaseName = "db1001"
    DefaultDatabase = "default1"

    if not db_id == None:

        db_id = db_id[0] + 1

        num = 1000 + int(db_id)

        DatabaseName = "db" + str(num)

        DefaultDatabase = 'default'+str(db_id)
    else:
        db_id = 1

        

    # sql = "INSERT INTO db_store(CompanyName, address1, address2, address3, username, password, city, state, country, postalcode, phone, mobile, email, website, currency, fractionalunit, vatnumber, gstnumber, tax1, tax2, tax3, customerid, host, port, DatabaseName, DefaultDatabase) VALUES ('"+companyname+"','"+address1+"','"+address2+"','"+address3+"','"+username+"','"+password+"','"+city+"','"+state+"','"+country+"','"+postalcode+"','"+telephone+"','"+mobile+"','"+email+"','"+website+"','"+currency+"','"+fractionalunit+"','"+vatnumber+"','"+gstnumber+"','"+tax1+"','"+tax2+"','"+tax3+"','"+customerid+"','"+host+"','"+port+"','"+DatabaseName+"','"+DefaultDatabase+"');" 
    # cursor.execute(sql)
    DatabaseStore.objects.create(
        DefaultDatabase = DefaultDatabase,
        DatabaseName = DatabaseName,
        CompanyName = companyname,
        Address1 = address1,
        Address2 = address2,
        Address3 = address3,
        username = username,
        password = password,
        city = city,
        state = state,
        country = country,
        postalcode = postalcode,
        phone = telephone,
        mobile = mobile,
        email = email,
        website = website,
        currency = currency,
        fractionalunit = fractionalunit,
        vatnumber = vatnumber,
        gstnumber = gstnumber,
        tax1 = tax1,
        tax2 = tax2,
        tax3 = tax3,
        customerid = customerid,
        host = host,
        port = port,
        )

    # res_id = cursor.fetchone()[0]
    # migration_db = 'default'+str(res_id)


    connection.commit()
    cursor.close()
    connection.close()

    con = psycopg2.connect(
        database= database,
        user= user, 
        password= password,
        host = host, 
        port = port
    )

    cursor_cred = con.cursor();
    con.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT);
    
    sqlCreateDatabase = "create database "+DatabaseName+";"
    cursor_cred.execute(sqlCreateDatabase);
    
    cursor_cred.close()
    con.close()

    success = True

    DATABASES = get_DBS()


    return db_id

