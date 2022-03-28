# misp-metrics

- InfluxDB 2.1: Time series database for storing MISP metrics 
    - URL: http://localhost:8086
- Grafana: For the UI and dashboards
    - URL: http://localhost:3000
- Loki: Parses logs and push them to InfluxDB
  - Apache
- Prometheus:
  - 
- Telegraf: Agent for pushing metrics to InfluxDB
  - Nginx
  - MySQL / MariaDB
  - Redis
  - Syslog




## Installation
composer install influxdata/influxdb-client-php


### Mysql/Mariadb performance
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



## MetricsComponent.php

### $this->Metrics->writeApi()

### $this->Metrics->writeSql()


## TODO
Done:- 
- Enable/disable by conf
- Set write timeout (5ms?)
- Add Grafana to docker

TODO:
- Load apache/nginx logs/data
- Clean docker-compose credentials






# InfluxDB v1 compatibility
docker-compose exec influxdb bash
influx v1 dbrp create \
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
  	
grafana:grafana123
  	
Token myusernametoken:passwordpasswordpassword