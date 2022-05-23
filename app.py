import numpy as np
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
import datetime as dt
from flask import Flask, jsonify


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")
# engine = create_engine("sqlite:////Resouces/hawaii.sqlite")
# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)
# # View all of the classes that automap found
# Base.classes.keys()
# Save reference to the table
Measurement = Base.classes.measurement
Station=Base.classes.station


#################################################
# Flask Setup
#################################################
app = Flask(__name__)


#################################################
# Flask Routes
#################################################

@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs <br/>"
         f"For below add any date you like to the end of the URL in this format<b>'/api/v1.0/2016-08-23'</b>starting from 2010 <br/>"
        f"/api/v1.0/<start><br/>"
        f"For below add any start and date you like to the end of the URL in this format <b>'/api/v1.0/2016-08-23/2017-08-23'</b> starting from 2010 <br/>"
        f"/api/v1.0/<start>/<end><br/>"
    )
#### THis route doesn't work!
@app.route("/api/v1.0/precipitation")
def precipitation():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Convert the query results to a dictionary using date as the key and prcp as the value.
    recent = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    recent_dt=dt.datetime.strptime(recent[0], "%Y-%m-%d")
    # Calculate the date one year from the last date in data set.
    recent_dt12mo=dt.date(recent_dt.year-1,recent_dt.month,recent_dt.day)
    #Perform a query to retrieve the data and precipitation scores
    sel=[Measurement.date,Measurement.prcp]
    date_prcp_res=session.query(*sel).filter(Measurement.date>=recent_dt12mo).all()

    session.close()

    # Create a dictionary from the row data and append to a list 
    precipitation_data = []
    for date, prcp in date_prcp_res:
        date_prcp_dic={}
        date_prcp_dic['date']=date
        date_prcp_dic['prcp']=prcp
        precipitation_data.append(date_prcp_dic)

# Return the JSON representation of your dictionary.
    return jsonify(precipitation_data)

#Return a JSON list of stations from the dataset.

@app.route("/api/v1.0/stations")
def stations():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Query all stations
    results2 = session.query(Station.station, Station.name).all()

    session.close()
    # Convert list of tuples into normal list
    station_data = list(np.ravel(results2))
# Return the JSON representation of your dictionary.
    return jsonify(station_data)  


#Query the dates and temperature observations of the most active station for the previous year of data.
#Return a JSON list of temperature observations (TOBS) for the previous year.
@app.route("/api/v1.0/tobs")
def tobs():
    # Create our session (link) from Python to the DB
    session = Session(engine)
    recent = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    recent_dt=dt.datetime.strptime(recent[0], "%Y-%m-%d")
    # # Calculate the date one year from the last date in data set.
    recent_dt12mo=dt.date(recent_dt.year-1,recent_dt.month,recent_dt.day)
    sel=[Measurement.date,Measurement.tobs]
    date_tobs_res=session.query(*sel).filter(Measurement.date>=recent_dt12mo).filter(Measurement.station=='USC00519281').all()
    print(date_tobs_res)
    session.close()
    tobs_data = []
    for date, tobs in date_tobs_res:
        date_tobs_dic={}
        date_tobs_dic['date']=date
        date_tobs_dic['tobs']=tobs
        tobs_data.append(date_tobs_dic)
    return jsonify(tobs_data)

@app.route("/api/v1.0/<start>")
def stats(start):
    # Create our session (link) from Python to the DB
    #this is to input a date and return the tmin, tmax, tavg of that date
    session = Session(engine)
    start_res=session.query(func.min(Measurement.tobs).label('to_obs_min'), func.max(Measurement.tobs).label('to_obs_max'), func.avg(Measurement.tobs).label('to_obs_avg')).filter(Measurement.date >= start).all()
    session.close()
    start_data = []
    for r in start_res:
        start_dic={}
        start_dic['to_obs_min']=r.to_obs_min
        start_dic['to_obs_max']=r.to_obs_max
        start_dic['to_obs_avg']=r.to_obs_avg
        start_data.append(start_dic)
    return jsonify(f"Chosen Start date:{start}",start_data)

@app.route("/api/v1.0/<start>/<end>")
def stats_start_end(start,end):
    # Create our session (link) from Python to the DB
    #this is to input a date and return the tmin, tmax, tavg of that date
    session = Session(engine)
    start_end=session.query(func.min(Measurement.tobs).label('to_obs_min'), func.max(Measurement.tobs).label('to_obs_max'), func.avg(Measurement.tobs).label('to_obs_avg')).filter(Measurement.date >= start).filter(Measurement.date <= end).all()
    session.close()
    start_end_data = []
    for r in start_end:
        start_end_dic={}
        start_end_dic['to_obs_min']=r.to_obs_min
        start_end_dic['to_obs_max']=r.to_obs_max
        start_end_dic['to_obs_avg']=r.to_obs_avg
        start_end_data.append(start_end_dic)
    return jsonify(f"Chosen Start date:{start} & Chosen End date:{end}",start_end_data)

if __name__ == '__main__':
    app.run(debug=True)
