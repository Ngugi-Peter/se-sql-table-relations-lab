# SQL Library and Pandas Library
import sqlite3
import pandas as pd

# Connect to the database
conn = sqlite3.connect('data.sqlite')

pd.read_sql("""SELECT * FROM sqlite_master""", conn)

# =====================================================================
# Part 1: Join and Filter
# =====================================================================

# STEP 1
# First name and job title for all employees in Boston
df_boston = pd.read_sql(
    """
    SELECT e.firstName, e.jobTitle
    FROM employees AS e
    JOIN offices AS o
        ON e.officeCode = o.officeCode
    WHERE o.city = 'Boston'
    """,
    conn,
)

# STEP 2
# Offices that have zero employees
df_zero_emp = pd.read_sql(
    """
    SELECT o.officeCode, o.city, o.state, o.country
    FROM offices AS o
    LEFT JOIN employees AS e
        ON o.officeCode = e.officeCode
    GROUP BY o.officeCode, o.city, o.state, o.country
    HAVING COUNT(e.employeeNumber) = 0
    """,
    conn,
)

# =====================================================================
# Part 2: Type of Join
# =====================================================================

# STEP 3
# All employees (even without an office) with their office's city and state,
# ordered by first name, then last name
df_employee = pd.read_sql(
    """
    SELECT e.firstName, e.lastName, o.city, o.state
    FROM employees AS e
    LEFT JOIN offices AS o
        ON e.officeCode = o.officeCode
    ORDER BY e.firstName, e.lastName
    """,
    conn,
)

# STEP 4
# Customers who have not placed an order, with their sales rep's employee
# number, sorted by the contact's last name
df_contacts = pd.read_sql(
    """
    SELECT c.contactFirstName, c.contactLastName, c.phone,
           c.salesRepEmployeeNumber
    FROM customers AS c
    LEFT JOIN orders AS o
        ON c.customerNumber = o.customerNumber
    WHERE o.orderNumber IS NULL
    ORDER BY c.contactLastName
    """,
    conn,
)

# =====================================================================
# Part 3: Built-In Function
# =====================================================================

# STEP 5
# Customer contacts with their payment dates and amounts, sorted by amount
# (high to low). amount is stored as text, so CAST it to a number to sort.
df_payment = pd.read_sql(
    """
    SELECT c.contactFirstName, c.contactLastName, p.paymentDate, p.amount
    FROM customers AS c
    JOIN payments AS p
        ON c.customerNumber = p.customerNumber
    ORDER BY CAST(p.amount AS REAL) DESC
    """,
    conn,
)

# =====================================================================
# Part 4: Joining and Grouping
# =====================================================================

# STEP 6
# Employees whose customers have an average credit limit over 90k,
# with their number of customers, sorted high to low
df_credit = pd.read_sql(
    """
    SELECT e.employeeNumber, e.firstName, e.lastName,
           COUNT(c.customerNumber) AS n_customers
    FROM employees AS e
    JOIN customers AS c
        ON e.employeeNumber = c.salesRepEmployeeNumber
    GROUP BY e.employeeNumber, e.firstName, e.lastName
    HAVING AVG(c.creditLimit) > 90000
    ORDER BY n_customers DESC
    """,
    conn,
)

# STEP 7
# Product popularity: number of orders and total units sold per product,
# sorted by total units (high to low)
df_product_sold = pd.read_sql(
    """
    SELECT p.productName,
           COUNT(od.orderNumber) AS numorders,
           SUM(od.quantityOrdered) AS totalunits
    FROM products AS p
    JOIN orderdetails AS od
        ON p.productCode = od.productCode
    GROUP BY p.productCode, p.productName
    ORDER BY totalunits DESC
    """,
    conn,
)

# =====================================================================
# Part 5: Multiple Joins
# =====================================================================

# STEP 8
# Number of different customers who ordered each product,
# sorted by the highest number of purchasers
df_total_customers = pd.read_sql(
    """
    SELECT p.productName, p.productCode,
           COUNT(DISTINCT o.customerNumber) AS numpurchasers
    FROM products AS p
    JOIN orderdetails AS od
        ON p.productCode = od.productCode
    JOIN orders AS o
        ON od.orderNumber = o.orderNumber
    GROUP BY p.productCode, p.productName
    ORDER BY numpurchasers DESC
    """,
    conn,
)

# STEP 9
# Number of customers per office, with the office code and city
df_customers = pd.read_sql(
    """
    SELECT COUNT(c.customerNumber) AS n_customers,
           o.officeCode, o.city
    FROM offices AS o
    JOIN employees AS e
        ON o.officeCode = e.officeCode
    JOIN customers AS c
        ON e.employeeNumber = c.salesRepEmployeeNumber
    GROUP BY o.officeCode, o.city
    """,
    conn,
)

# =====================================================================
# Part 6: Subquery
# =====================================================================

# STEP 10
# Employees who sold products that were ordered by fewer than 20 customers.
# The subquery finds the products ordered by 19 or fewer different customers.
df_under_20 = pd.read_sql(
    """
    SELECT DISTINCT e.employeeNumber, e.firstName, e.lastName,
           o.city, o.officeCode
    FROM employees AS e
    JOIN offices AS o
        ON e.officeCode = o.officeCode
    JOIN customers AS c
        ON e.employeeNumber = c.salesRepEmployeeNumber
    JOIN orders AS ord
        ON c.customerNumber = ord.customerNumber
    JOIN orderdetails AS od
        ON ord.orderNumber = od.orderNumber
    WHERE od.productCode IN (
        SELECT od2.productCode
        FROM orderdetails AS od2
        JOIN orders AS o2
            ON od2.orderNumber = o2.orderNumber
        GROUP BY od2.productCode
        HAVING COUNT(DISTINCT o2.customerNumber) < 20
    )
    ORDER BY e.lastName, e.firstName
    """,
    conn,
)

# STEP 11
# Close the connection
conn.close()