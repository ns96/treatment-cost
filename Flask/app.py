# Basic flask app to provide an API for the surgery cost dataset
# Dataset: https://data.world/dmikebishop/surgery-charges-across-the-u-s
# DRG Difinition: https://www.verywellhealth.com/drg-101-what-is-a-drg-how-does-it-work-3916755
# @author Nathan Stevens
# @version 1.0

# Import the dependencies.
import sys
from sqlalchemy import create_engine, text
from flask import Flask, jsonify, render_template
from flask_cors import CORS

#################################################
# Database Setup, either sqlite or postgresql
#################################################

# macos/linux
engine = create_engine("sqlite:///../Data/SurgeryCharges.sqlite3")

# windows
#engine = create_engine("sqlite:///..\\Data\\SurgeryCharges.sqlite3")

# RECOMMENDED
#engine = create_engine('postgresql+psycopg2://postgres:postgres@localhost/SurgeryCharges')

# make sure we can connect to the database, otherwise exit
try:
  conn = engine.connect()
  conn.close()
except Exception as e:
  print("DB Connection Error\n")    
  print(e)
  sys.exit()

#################################################
# Flask Setup
#################################################
app = Flask(__name__)
CORS(app)

#################################################
# Flask Routes
#################################################
@app.route("/")
def welcome():
    """List all available api routes."""
    
    return (
        f"<b>Available Routes:</b><br/><br>"
        f"<b>/api/v1.0/drg/&lt;drg_id&gt;</b> [ get all DRG records group by state ]<br/>"
        f"<b>/api/v1.0/categories</b> [ get the main categories ]<br/>"
        f"<b>/api/v1.0/definitions/&lt;category&gt;</b> [ get all the DRG definitions for a particular category ]<br/>"
        f"<b>/api/v1.0/stats</b> [ get basic DRG statistics group by state ]<br/>"
        f"<b>/api/v1.0/top/providers/&lt;limit&gt;</b> [ get top n providers by patient discharges nation wide ]<br/>"        
        f"<b>/api/v1.0/providers/&lt;state&gt;</b> [ get all providers in a state ]<br/>"
        f"<b>/api/v1.0/providers/&lt;state&gt;/&lt;drg_id&gt; </b>[ get all providers in a state for a particular DRG ]<br/><br/>"
        f"<b>/view </b>[ <a href='/view'> view the basic web UI </a>]<br/>"
    )

@app.route("/api/v1.0/drg/<drg_id>")
def drg_all(drg_id):
    """
    Return the drg data for all the states
    """
    query = text('SELECT "Provider State", COUNT(*), SUM("Total Discharges"), '\
                 'AVG("Average Total Payments"), AVG("Average Medicare Payments") '\
                 'FROM "DRG_RECORDS" '\
                 'INNER JOIN "PROVIDERS" '\
                 'ON "PROVIDERS"."Provider Id" = "DRG_RECORDS"."Provider Id" '\
                 'WHERE "DRG Id" = ' + drg_id + ' '\
                 'GROUP BY "Provider State"')
    print(query)
    
    with engine.connect() as conn:
      results = conn.execute(query).fetchall()
    
    records = dict()
    
    for row in results:
      record = dict()
      record["state"] = row[0]
      record["count"] = row[1]
      record["discharges"] = row[2]
      record["avg_payments"] = int(row[3])
      record["avg_medicare"] = int(row[4])
      record["avg_difference"] = int(row[3] - row[4])
      
      # calcuate the percent medicare payments
      pct = int((row[4]/row[3])*100)
      record["pct_medicare"] = pct
      
      records[row[0]] = record # add to dictionary
    
    return jsonify(records)

@app.route("/api/v1.0/categories")
def drg_categories():
    """ 
    Return the drg categories
    """
    query = text('SELECT "Category", COUNT(*) '\
                 'FROM "DRG" '\
                 'GROUP BY "Category" '\
                 'ORDER BY COUNT(*) DESC')
    print(query)
    with engine.connect() as conn:
      results = conn.execute(query).fetchall()
    
    categories = []
    for row in results:
      categories.append({row[0]: row[1]})
    
    return jsonify(categories)

@app.route("/api/v1.0/definitions/<category>")
def drg_definitions(category):
    """ 
    Return the drg definitions for a particular category
    """
    query = text("SELECT * FROM \"DRG\" WHERE \"Category\" = " + "'" + category + "'")
    print(query)
    with engine.connect() as conn:
      results = conn.execute(query).fetchall()
    
    definitions = []
    for row in results:
      definition = dict()
      definition["value"] = row[0]
      definition["text"] = row[1]
      definitions.append(definition)
    
    return jsonify(definitions)

@app.route("/api/v1.0/stats")
def drg_stats():
    """
    Return the stats nation wide group by the drg so you can what the most
    popular surgery/procedure is etc
    """
    
    query = text('SELECT MIN("DRG"."DRG Id"), "DRG Definition", '\
                 'COUNT(*), SUM("Total Discharges"), '\
                 'AVG("Average Total Payments"), '\
                 'AVG("Average Medicare Payments") '\
                 'FROM "DRG_RECORDS" '\
                 'INNER JOIN "DRG" '\
	             'ON "DRG"."DRG Id" = "DRG_RECORDS"."DRG Id" '\
                 'GROUP BY "DRG Definition" ')
    print(query)
    
    with engine.connect() as conn:
      results = conn.execute(query).fetchall()
    
    records = dict()
    
    for row in results:
      record = dict()
      record["drg_id"] = int(row[0])
      record["drg_definition"] = row[1]
      record["count"] = row[2]
      record["discharges"] = row[3]
      record["avg_payments"] = int(row[4])
      record["avg_medicare"] = int(row[5])
      record["avg_difference"] = int(row[4] - row[5])
      
      # calcuate the percent medicare payments
      pct = int((row[5]/row[4])*100)
      record["pct_medicare"] = pct
      
      records[int(row[0])] = record # add to dictionary
    
    return jsonify(records)

@app.route("/api/v1.0/top/providers/<limit>")
def top_providers(limit):
    """
    Return the the top n providers nation wide grouping by state and provider
    """
    query = text('SELECT "Provider State", "Provider Name", COUNT(*), SUM("Total Discharges"), '\
                 'AVG("Average Total Payments"), AVG("Average Medicare Payments"), '\
                 'MIN("latitude"), MIN("longitude") '\
                 'FROM "DRG_RECORDS" '\
                 'INNER JOIN "PROVIDERS" '\
	             'ON "PROVIDERS"."Provider Id" = "DRG_RECORDS"."Provider Id" '\
                 'INNER JOIN "DRG" '\
	             'ON "DRG"."DRG Id" = "DRG_RECORDS"."DRG Id" '\
                 'GROUP BY "Provider State", "Provider Name" '\
                 'ORDER BY SUM("Total Discharges") DESC LIMIT ' + limit)
    print(query)
    
    with engine.connect() as conn:
      results = conn.execute(query).fetchall()
    
    providers = []
    for row in results:
      provider = dict()
      
      provider["state"] = row[0]
      provider["name"] = row[1]
      provider["drg_count"] = row[2]
      provider["discharges"] = row[3]
      provider["avg_payments"] = int(row[4])
      provider["avg_medicare"] = int(row[5])
      provider["avg_difference"] = int(row[4] - row[5])
      
      # calcuate the percent medicare payments
      pct = int((row[5]/row[4])*100)
      provider["pct_medicare"] = pct
      provider["latitude"] = row[6]
      provider["longitude"] = row[7]
      
      providers.append(provider)
    
    return jsonify(providers)

@app.route("/api/v1.0/providers/<state>")
def providers_for_state(state):
    """
    Return the all providers for a particular state
    """
    query = text('SELECT "Provider Name", COUNT(*), SUM("Total Discharges"), '\
                 'AVG("Average Total Payments"), AVG("Average Medicare Payments"), '\
                 'MIN("latitude"), MIN("longitude") '\
                 'FROM "DRG_RECORDS" '\
                 'INNER JOIN "PROVIDERS" '\
	             'ON "PROVIDERS"."Provider Id" = "DRG_RECORDS"."Provider Id" '\
                 'INNER JOIN "DRG" '\
	             'ON "DRG"."DRG Id" = "DRG_RECORDS"."DRG Id" '\
                 "WHERE \"Provider State\" = '" + state + "' "\
                 'GROUP BY "Provider Name"')
    print(query)
    
    with engine.connect() as conn:
      results = conn.execute(query).fetchall()
    
    providers = []
    for row in results:
      provider = dict()
      
      provider["state"] = state
      provider["name"] = row[0]
      provider["drg_count"] = row[1]
      provider["discharges"] = row[2]
      provider["avg_payments"] = int(row[3])
      provider["avg_medicare"] = int(row[4])
      provider["avg_difference"] = int(row[3] - row[4])
      
      # calcuate the percent medicare payments
      pct = int((row[4]/row[3])*100)
      provider["pct_medicare"] = pct
      provider["latitude"] = row[5]
      provider["longitude"] = row[6]
      
      providers.append(provider)
    
    return jsonify(providers)
  
@app.route("/api/v1.0/providers/<state>/<drg_id>")
def providers(state, drg_id):
    """
    Return the providers in a state for a particular drg
    """
    query = text('SELECT "Provider State", "Provider Name", "DRG Definition", '\
	             '"Total Discharges", "Average Total Payments", '\
	             '"Average Medicare Payments", "latitude", "longitude" '\
                 'FROM "DRG_RECORDS" '\
                 'INNER JOIN "PROVIDERS" '\
	             'ON "PROVIDERS"."Provider Id" = "DRG_RECORDS"."Provider Id" '\
                 'INNER JOIN "DRG" '\
	             'ON "DRG"."DRG Id" = "DRG_RECORDS"."DRG Id" '\
                 "WHERE \"Provider State\" = '" + state + "' AND \"DRG_RECORDS\".\"DRG Id\" = " + drg_id)
    print(query)
    
    with engine.connect() as conn:
      results = conn.execute(query).fetchall()
    
    providers = []
    for row in results:
      provider = dict()
      
      provider["drg_id"] = drg_id
      provider["state"] = row[0]
      provider["name"] = row[1]
      provider["drg"] = row[2]
      provider["discharges"] = row[3]
      provider["avg_payments"] = int(row[4])
      provider["avg_medicare"] = int(row[5])
      provider["avg_difference"] = int(row[4] - row[5])
      
      # calcuate the percent medicare payments
      pct = int((row[5]/row[4])*100)
      provider["pct_medicare"] = pct
      provider["latitude"] = row[6]
      provider["longitude"] = row[7]
      
      providers.append(provider)
    
    return jsonify(providers)

@app.route("/view")
def view_ui():
    """
    Return the html page to view basic site UI
    """
    
    version = "v1.0.6"
    year = "2014"
    return render_template('index.html', version=version, year=year)

# start the application if it running in the console on port 5015 so localhost
# works on newer macs
if __name__ == '__main__':
    app.run(debug=True, host = '0.0.0.0', port=5015)