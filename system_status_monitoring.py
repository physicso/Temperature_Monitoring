import psutil,datetime,time,socket,MySQLdb,fcntl,struct

def get_ip_address(ifname):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    return socket.inet_ntoa(fcntl.ioctl(
        s.fileno(),
        0x8915,  # SIOCGIFADDR
        struct.pack('256s', ifname[:15])
    )[20:24])

def writeIntoDb(sql):
    try:
        conn=MySQLdb.connect(host='10.1.0.5',user='root',passwd='root123',db='monitor',port=3306)
        cur=conn.cursor()
        cur.execute(sql)
	conn.commit()
        cur.close()
        conn.close()
    except MySQLdb.Error,e:
	output = open('/home/lihu/monitor/status.txt','a')
        output.write("\nSQL: %s\n" % (sql))
        output.write("Mysql Error %d: %s" % (e.args[0], e.args[1]))
        output.close()
        output = open('/home/lihu/monitor/status.sql','a')
        output.write("%s\n" % (sql))
        output.close()

def collectStatus():
    second = 5 # Time tick for counting.

    # Get date and time
    
    time_on_written = datetime.datetime.now()
    date_time = time_on_written.strftime('%Y-%m-%d %H:%M:%S')
    
    # Get IP address.

    IP = get_ip_address("eth0")

    # CPU usage of all the cores (threads) in one server.

    cpu_usage = psutil.cpu_percent(interval=1)

    # Memory usage

    swap_memory_usage = psutil.swap_memory()[3]
    physical_memory_usage = psutil.virtual_memory()[2]

    # Hard disk usage: data input and data output among all the disks (bytes/second).
    # Network usage: data transfered in and out (bytes/second).
    
    input_before_sleep = psutil.disk_io_counters()[2]
    output_before_sleep = psutil.disk_io_counters()[3]
    in_before_sleep = psutil.net_io_counters()[0]
    out_before_sleep = psutil.net_io_counters()[1]
    time.sleep(second)
    input_after_sleep = psutil.disk_io_counters()[2]
    output_after_sleep = psutil.disk_io_counters()[3]
    in_after_sleep = psutil.net_io_counters()[0]
    out_after_sleep = psutil.net_io_counters()[1]

    data_input = (input_after_sleep - input_before_sleep)/5
    data_output = (output_after_sleep - output_before_sleep)/5

    net_in = (in_after_sleep - in_before_sleep)/5
    net_out = (out_after_sleep - out_before_sleep)/5

    # Write the status data into the database

    sql = 'insert into status (ip,dtime,cpu,pmemory,smemory,diskin,diskout,netin,netout) values (\''+str(IP)+'\',\''+date_time+'\','+str(cpu_usage)+','+str(physical_memory_usage)+','+str(swap_memory_usage)+','+str(data_input)+','+str(data_output)+','+str(net_in)+','+str(net_out)+');'
    writeIntoDb(sql)

# Start iteration in EXACTLY every five minutes.
if __name__ == "__main__":
	collectStatus()
