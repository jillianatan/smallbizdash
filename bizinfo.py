#imports
import os
from dotenv import load_dotenv
from supabase import create_client, Client
import streamlit as st
import pandas as pd

#load env 
load_dotenv()

#create supabase client 
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

#functions
#functions that add rows to the database
def new_product(baseItem, style, estCost, colorID, collId):
    result = supabase.table("products").insert(
        {
            "base_item": baseItem, 
            "type": style, 
            "price_cost_make": estCost,
            "coll_id": collId,
            }).execute()
    supabase.table("prod_color").insert({"color_id": colorID, "prod_id": result.data[0]["prod_ID"]}).execute()
    return ("Product added successfully with ID: " + str(result.data[0]["prod_ID"]))
#new event function
def new_event(eventName, eventType, eventlen):
    result = supabase.table("event").insert(
        {
            "event_name": eventName, 
            "event_type": eventType,
            "event_len_hrs": eventlen,
            }).execute()
    return ("Event added successfully with ID: " + str(result.data[0]["event_id"]))
#add sale function
def new_sale(prodID, eventID, salePrice, qt):
    result = supabase.table("sales").insert(
        {
            "event_id": eventID, 
            }).execute()
    r2 = supabase.table("lineItems").insert(
        {
            "sale_id": result.data[0]["sale_id"], 
            "prod_id": prodID, 
            "sale_price": salePrice, 
            "qt": qt
            }).execute()
    return ("Sale added successfully with ID: " + str(result.data[0]["sale_id"]))
#add inventory change function
def new_inv_change(amtMade, amtSold, prodID):
    result = supabase.table("inventory_changes").insert(
        {
            "amt_made": amtMade, 
            "amt_sold": amtSold, 
            "prod_id": prodID
            }).execute()
    return ("Inventory change added successfully with ID: " + str(result.data[0]["id"]))

#functions that search for info in the database
#function that searches for #avail 
def search_inv(prodID):
    retInv = supabase.table("inventory_changes").select("amt_made, amt_sold").eq("prod_id", prodID).execute()
    if not retInv.data:
        return ("No inventory records found for product ID: " + str(prodID))
    sumMade = 0
    sumSold = 0
    for i in range(len(retInv.data)):
        sumMade += retInv.data[i]["amt_made"]
        sumSold += retInv.data[i]["amt_sold"]
    retSum = sumMade - sumSold
    return (retSum)
#function that searches for product information
def search_prod(baseItem, style, colorID, collId):
    retId = supabase.table("products").select("prod_ID").eq("base_item", baseItem).eq("type", style).eq("coll_id", collId).execute()
    for row in retId.data:
        prodID = row["prod_ID"]
        retColor = supabase.table("prod_color").select("color_id").eq("prod_id", prodID).execute()
        if retColor.data and retColor.data[0]["color_id"] == colorID:
            return (prodID)
    if not retId.data:
        return ("Product not found.")
    return (retId.data[0]["prod_ID"])

#analytics functions
#total num of sales function
def total_sales():
    retSales = supabase.table("sales").select("*", count="exact").execute()
    return (len(retSales.data))
#total revenue function
def total_revenue():
    retLineItems = supabase.table("lineItems").select("sale_price, qt",).execute()
    totalRev = 0
    for i in range(len(retLineItems.data)):
        totalRev += retLineItems.data[i]["sale_price"] * retLineItems.data[i]["qt"]
    return (totalRev)
#item sold most times  
def most_sales_item_indv():
    mostsales = (
        supabase.table("mostsales")
        .select("*")
        .execute()
    )
    return (mostsales.data[0]["prod_id"])
#item with most sales
def mostSalesItem():
    #numsales = supabase.rpc("mostsales").execute()
    numsales = (
    supabase.table("mostorders")
        .select("*")
        .execute()
    )
    return (numsales.data[0]["prod_id"])
#item that bring most revenue
def mostRevenue():
    #mostrev = supabase.rpc("mostrevenue").execute()
    mostrev = supabase.table("totalrev").select("*").execute()
    return (mostrev.data[0]["prod_id"])
#totalexp
def total_exp():
    #totalexpenses = supabase.rpc("totalexp").execute()
    totalexpenses = supabase.table("totalexp").select("*").execute()
    return (totalexpenses.data[0]["totalexp"])
#event with most revenue
def mostRevEvent():
    mostrevevent = supabase.table("top_event_rev").select("*").execute()
    return (mostrevevent.data[0]["event_id"])
#event with most revenue per hour
def mostRevEventHr():
    mostreveventh = supabase.table("revbyevent").select("*").execute()
    return (mostreveventh.data[0]["event_id"])

#chart stuff
def barchartrevbyprod():
    revbyprod = supabase.table("revperitem").select("*").execute().data
    df = pd.DataFrame(revbyprod)
    return df
#create page

st.sidebar.title("Navigation")
with st.sidebar:
    page = st.radio("Go to", ["Search", "Add New Info", "Analytics", "Charts", "Info"])

def search():
    st.title("Search for Information Here")
    #product search: id, baseItem, style, estCost, colorID, collId, # avail 
    st.subheader("Given ID, return inventory available")
    st.text_input("Product ID", key="prodID")
    if st.button("Search by ID"):   
        retInv = search_inv(st.session_state.prodID)
        st.write("Number Available: " + str(retInv))
    st.subheader("Given product info, return product ID")
    st.text_input("Base Item", key="baseItem")
    st.text_input("Style", key="style")
    st.text_input("Color ID", key="colorID")
    st.text_input("Collection ID", key="collId")
    if st.button("Search by Product Info"):
        retProd = search_prod(st.session_state.baseItem, st.session_state.style, st.session_state.colorID, st.session_state.collId)
        st.write("Product ID: " + str(retProd))
    
def add():
    st.title("Add New Info Here")
    st.subheader("Add new product")
    st.text_input("Base Item", key="baseItem")
    st.text_input("Style", key="style")
    st.text_input("Estimated Cost to Make", key="estCost")
    st.text_input("Color ID", key="colorID")
    st.text_input("Collection ID", key="collId")
    if st.button("Add Product"):
        result = new_product(st.session_state.baseItem, st.session_state.style, st.session_state.estCost, st.session_state.colorID, st.session_state.collId)
        st.write(result)
    st.subheader("Add new event")
    st.text_input("Event Name", key="eventName")
    st.text_input("Event Type", key="eventType")
    st.text_input("Event Length in Hours", key="eventlen")
    if st.button("Add Event"):
        result = new_event(st.session_state.eventName, st.session_state.eventType, st.session_state.eventlen)
        st.write(result)
    st.subheader("Add new sale")
    st.text_input("Product ID", key="prodID")
    st.text_input("Event ID", key="eventID")
    st.text_input("Sale Price", key="salePrice")
    st.text_input("Quantity Sold", key="qt")
    if st.button("Add Sale"):
        result = new_sale(st.session_state.prodID, st.session_state.eventID, st.session_state.salePrice, st.session_state.qt)
        inventoryChange = new_inv_change(0, st.session_state.qt, st.session_state.prodID)
        #add inventory change for the sale 
        st.write(result)    
    st.subheader("Add new inventory change")
    st.text_input("Amount Made", key="amtMade")
    st.text_input("Product ID", key="prodID2")
    if st.button("Add Inventory Change"):
        result = new_inv_change(st.session_state.amtMade, 0, st.session_state.prodID2)
        st.write(result)

def analytics():
    st.title("Analytics Page")
    st.write("Total Number of Sales: " + str(total_sales()))
    st.write("Total Revenue: " + str(total_revenue()))
    st.write("Item Sold Most Times: " + str(most_sales_item_indv()))
    st.write("Item with Most Sales: " + str(mostSalesItem()))
    st.write("Item that Brings Most Revenue: " + str(mostRevenue()))
    st.write("Total Expenses: " + str(total_exp()))
    st.write("Event with Most Revenue: " + str(mostRevEvent()))
    st.write("Event with Most Revenue per Hour: " + str(mostRevEventHr()))

def charts():
    st.title("Charts Page")
    st.write("Revenue by Product: (bar chart)")
   # st.write(supabase.table("revperitem").select("*").execute().data)
   # st.write(barchartrevbyprod())
    st.bar_chart(barchartrevbyprod())

def info():
    st.title("Info Page")
    st.write("naming conventions")
    st.write("ids except for product id are with snake case _")
    st.write("List of colors and their corresponding colorIDs:")
    st.write("1 white 2 pink 3 blue 4 purple 5 green 6 yellow")
    st.write("List of collections and their corresponding collIDs:")

    #create expandable 
if page == "Search":
    search()            
elif page == "Add New Info":
    add()
elif page == "Analytics":
     analytics()
elif page == "Charts":
    charts()
elif page == "Info":
    info()


