# TwistedWeb imports
from twisted.web.server import Site
from twisted.web.resource import Resource
from twisted.internet import reactor

# Matplotlib and MPLD3 imports
import matplotlib.pylab as plt
import matplotlib.dates as mdate
import mpld3

# Influxdb imports
from influxdb import InfluxDBClient
import numpy as nps

#formats for time points are YYYY-MM-DD HH:MM:SS
def getIntervalPoints(string1, string2):
    db = InfluxDBClient('devonpi', '8086', 'root', 'root', 'power')
    dataquery = 'select instant_power from sensor where time > ' + '\'' + string1 + '\'' + ' and time < ' + '\'' + string2 + '\''
    result = db.query(dataquery)
    return result

#returns the last x entries with timestamps within the previous 'hours'
def getLastXPoints(hours, x):
    db = InfluxDBClient('devonpi', '8086', 'root', 'root', 'power')
    dataquery = 'select instant_power from sensor where time > now() - ' + str(hours) + 'h limit ' + str(x)
    result = db.query(dataquery)
    return result


class RootHandler(Resource):
    isLeaf = True

    def get_root(self, args):
        root_html = "<html><body><div align=\"left\">"
        root_html += "Welcome to the Smart Networked Power Meter!"
        root_html += "</div></body></html>"
        return root_html

    def render_GET(self, request):
        return self.get_root()

class RecentDataHandler(Resource):
    isLeaf = True

    def get_root(self, args):
        power_list = getLastXPoints(int(args["past_hours"][0]), int(args["num_points"][0]))
        print power_list
        x_axis_epoch = []
        y_axis = []
        if power_list != []:
            for point in power_list[0]["points"]:
                x_axis_epoch.append(point[0])
                y_axis.append(point[2])

        # Convert to the correct format for matplotlib.
        # mdate.epoch2num converts epoch timestamps to the right format for matplotlib
        secs = mdate.epoch2num(x_axis_epoch)

        fig, ax = plt.subplots()

        # Plot the date using plot_date rather than plot
        ax.plot_date(secs, y_axis)

        # Choose your xtick format string
        date_fmt = '%H:%M:%S'

        # Use a DateFormatter to set the data to the correct format.
        date_formatter = mdate.DateFormatter(date_fmt)
        ax.xaxis.set_major_formatter(date_formatter)

        # Sets the tick labels diagonal so they fit easier.
        fig.autofmt_xdate()

        plt.ylim(0, 80)
        plt.ylabel("Power Usage (W)")
        plt.xlabel("Time (UTC)")
        plt.title("Time vs Power Usage")

        fig.set_size_inches(12,8)

        root_html = "<html><body><div style=\"float:left\">"
        root_html += mpld3.fig_to_html(fig).encode("ascii")
        root_html += "</div><div style=\"float:right\"></br><bold>STATISTICS:</bold> </br>"
        root_html += "MIN Power: " + str(round(nps.min(y_axis), 6)) + " Watts </br>"
        root_html += "MAX Power: " + str(round(nps.max(y_axis), 6)) + " Watts </br>"
        root_html += "AVG Power: " + str(round(nps.average(y_axis), 6)) + " Watts </br>"
        root_html += "Energy Usage: " + str(round((nps.average(y_axis)*((nps.max(x_axis_epoch)-nps.min(x_axis_epoch))/float(60*60)))/1000, 6)) + " Kilowatt Hours </br>"
        root_html += "</div></body></html>"
        plt.close()
        return root_html

    def render_GET(self, request):
        print request.args
        if "past_hours" and "num_points" in request.args:
            return self.get_root(request.args)
        else:
            return "Please put the right arguments in.\n Syntax: /recentdata/?past_hours=X&num_points=Y"

class DateRangeHandler(Resource):
    isLeaf = True

    def get_root(self, args):
        power_list = getIntervalPoints(args["start_date"][0] + " 00:00:00", args["end_date"][0] + " 00:00:00")
        print power_list
        x_axis_epoch = []
        y_axis = []
        if power_list != []:
            for point in power_list[0]["points"]:
                x_axis_epoch.append(point[0])
                y_axis.append(point[2])

        # Convert to the correct format for matplotlib.
        # mdate.epoch2num converts epoch timestamps to the right format for matplotlib
        secs = mdate.epoch2num(x_axis_epoch)

        fig, ax = plt.subplots()

        # Plot the date using plot_date rather than plot
        ax.plot_date(secs, y_axis)

        # Choose your xtick format string
        date_fmt = '%H:%M:%S'

        # Use a DateFormatter to set the data to the correct format.
        date_formatter = mdate.DateFormatter(date_fmt)
        ax.xaxis.set_major_formatter(date_formatter)

        # Sets the tick labels diagonal so they fit easier.
        fig.autofmt_xdate()

        plt.ylim(0, 80)
        plt.ylabel("Power Usage (W)")
        plt.xlabel("Time (UTC)")
        plt.title("Time vs Power Usage")

        fig.set_size_inches(12,8)

        root_html = "<html><body><div style=\"float:left\">"
        root_html += mpld3.fig_to_html(fig).encode("ascii")
        root_html += "</div><div style=\"float:right\"></br><bold>STATISTICS:</bold> </br>"
        root_html += "MIN Power: " + str(round(nps.min(y_axis), 6)) + " Watts </br>"
        root_html += "MAX Power: " + str(round(nps.max(y_axis), 6)) + " Watts </br>"
        root_html += "AVG Power: " + str(round(nps.average(y_axis), 6)) + " Watts </br>"
        root_html += "Energy Usage: " + str(round((nps.average(y_axis)*((nps.max(x_axis_epoch)-nps.min(x_axis_epoch))/float(60*60)))/1000, 6)) + " Kilowatt Hours </br>"
        root_html += "</div></body></html>"
        plt.close()
        return root_html

    def render_GET(self, request):
        print request.args
        if "start_date" and "end_date" in request.args:
            return self.get_root(request.args)
        else:
            return "Please put the right arguments in.\n Syntax: /daterange/?start_date=YYYY-MM-DD&end_date=YYYY-MM-DD"


class SystemTime(Resource):
    isLeaf = True

    def render_GET(self, request):
        return "<html><body>The time of the server system clock when your GET request was processed: " + time.ctime() + "</body></html>"


root = Resource()
root.putChild("", RootHandler())
root.putChild("recentdata", RecentDataHandler())
root.putChild("daterange", DateRangeHandler())
root.putChild("systime", SystemTime())
factory = Site(root)
reactor.listenTCP(8880, factory)
reactor.run()