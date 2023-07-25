# Import the dependencies.
from flask import Flask, jsonify
import pandas as pd
import numpy as np
import datetime as dt

#Python SQL toolkit and Object Relational Mapper
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()

# reflect the tables
Base.prepare(engine, reflect = True)

#View all of the classes that automap found
#Base.classes.keys()

# Save references to each table
Measure = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
#################################################
#Create an app, being sure to pass _name_ 
app = Flask(__name__)



#################################################
# Flask Routes
#################################################
#Home route
@app.route("/") 
def home(): 
    " " "Home route that list all my route paths" " "
    return (
        f"Welcome to my HI Weather API<br/>"
        f"Avalible routes: <br/>"
        f"/api/v1.0/precipitation<br>"
        f"/api/v1.0/stations<br>"
        f"/api/v1.0/tobs<br>"
        f"/api/v1.0/start<br>"
        f"/api/v1.0/start/end<br>"
        f"Note: start and end must be dates in MMDDYYYY format with start and end"
    )

#Precipitation Route
@app.route("/api/v1.0/precipitation") 
def prcp_output(): 
    " " "Return precipitation information for the last 12 months in json format" " "
  
    # Calculate the date one year from the last date in data set.
    year_ago = dt.datetime(2017,8,23) - dt.timedelta(days=365)

    # Perform a query to retrieve the data and precipitation scores
    prcp_query = session.query(Measure.date, Measure.prcp).filter(Measure.date >= year_ago).all()

    # Close session
    session.close()
    
    precip = {date: prcp for date, prcp in prcp_query}
    
    # Return jsonify version of precip 
    return jsonify(precip)

#Station Route
@app.route("/api/v1.0/stations") 
def station_output(): 
    " " "Return list of stations" " "
    all_stations_results = session.query(Station.station).all()
    
    # Close session
    session.close()
    
    # Convert list of tuples into normal list 
    all_stations = list(np.ravel(all_stations_results))

    # Return jsonify version of precip 
    return jsonify(all_stations)

#Temperature Route
@app.route("/api/v1.0/tobs") 
def temp_output(): 
    """Return temperatures for the last year for the most active station:"""
    
    # Calculate the date one year from the last date in data set.
    year_ago = dt.datetime(2017,8,23) - dt.timedelta(days=365)
    
    # Query the last 12 months of temperature observation data for this station USC00519281
    most_active_station_query = session.query(Measure.tobs).\
        filter(Measure.station == 'USC00519281').\
        filter(Measure.date >= year_ago).all()
        
    # Close session
    session.close()
    
    #unravel results
    temperatures = list(np.ravel(most_active_station_query))
    
    # Return jsonify version of temperatures for last year for USC00519281
    return jsonify(temperatures = temperatures)

#start and stop and end route for temperatures USC00519281
@app.route("/api/v1.0/<start>") 
@app.route("/api/v1.0/<start>/<end>") 
def temp_start(start=None, end=None):
    """Return a JSON list of the minimum temperature, the average temperature, 
    and the maximum temperature for a specified start or start-end range."""
    
    #sel technique
    sel = [func.min(Measure.tobs), func.avg(Measure.tobs), func.max(Measure.tobs)]
    
    #two possible routes
    #start is provided (no end)
    if not end: 
    
        #transform start and end into date using dt.datetime
        start = dt.datetime.strptime(start, "%m%d%Y")

        temp_stats_results = session.query(*sel).\
            filter(Measure.station == 'USC00519281').\
                filter(Measure.date >= start).all()
            
        # Close session
        session.close()
        
        #unravel results
        temp_stats = list(np.ravel(temp_stats_results))
        
        # Return jsonify version of temperatures for last year for USC00519281
        return jsonify(min_avg_max = temp_stats)
    
    #start and end is provided
    #transform start and end into date using dt.datetime
    start = dt.datetime.strptime(start, "%m%d%Y")
    end = dt.datetime.strptime(end, "%m%d%Y")

    temp_stats_results = session.query(*sel).\
            filter(Measure.station == 'USC00519281').\
                filter(Measure.date >= start).\
                    filter(Measure.date <= end).all()
            
    # Close session
    session.close()
        
    #unravel results
    temp_stats = list(np.ravel(temp_stats_results))
    
    # Return jsonify version of temperatures for last year for USC00519281
    return jsonify(min_avg_max = temp_stats)
    
if __name__ == '__main__': 
    app.run(debug=True)