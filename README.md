# misp-metrics

- InfluxDB 2.1: Time series database for storing MISP metrics 
    - URL: http://localhost:8086
- Grafana: For the UI and dashboards
    - URL: http://localhost:3000
- Telegraf: Agent installed in the MISP instance for pushing metrics to InfluxDB
  - Nginx/Apache
  - MySQL/MariaDB
  - Redis

## Installation
composer install influxdata/influxdb-client-php

### Tracking MySQL/MariaDB performance
`$ sudo vim /etc/mysql/my.cnf`

```
[mysqld]
performance_schema=ON
performance-schema-instrument='stage/%=ON'
performance-schema-consumer-events-stages-current=ON
performance-schema-consumer-events-stages-history=ON
performance-schema-consumer-events-stages-history-long=ON
```

`sudo service mysql restart`

Add this to your `telegraf.conf` file:
```
[[inputs.mysql]]
  servers = ["user:password@tcp(127.0.0.1:3306)/"]
  metric_version = 2
```

### Config
1. Go to your InfluxDB UI:
http://localhost:8086/orgs/e8889e136b55933c/load-data/tokens

2. Copy the token and add it to the `Metrics.token`  MISP instance config.
```
'Metrics' => array(
        'enabled'=> false,
        'InfluxDB' => array(
        'url' => 'http://localhost:8086',
        'token' => 'MY_TOKEN',
        'bucket' => 'misp',
        'org' => 'myorg',
        'timeout' => 10,
        )
    ),
```

# InfluxDB v1 compatibility
Grab bucket-id from InfluxDB UI and:
```
$ docker-compose exec influxdb bash
$ influx v1 dbrp create \
  --db mydb \
  --rp mybucket-rp \
  --bucket-id d5c66ab09153ba05 \
  --default \
  -o myorg \
  -t mytoken
  
  
influx v1 auth create \
	--read-bucket d5c66ab09153ba05 \
	--write-bucket d5c66ab09153ba05 \
	--username grafana \
  	-o myorg \
  	-t mytoken
```