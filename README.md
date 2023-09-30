# elementor

I have created two applications, one which reads current cpu levels, and writes them to kafka topic "cpu_usage". you can find the code and dockerfile in the "cpu-monitor" folder.
the second app consumes the messages from kafka and writes them into a S3 bucket. the code and dockerfile are in the "consumer-s3" folder.

A helm chart for deploying the two applications was created and can be found  in the "cpu-chart" folder.

For the kafka cluster i used the bitnami helm chart, it's values file is named  kafka-values.yml.
