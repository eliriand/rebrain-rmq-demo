FROM rabbitmq:3.12-management

ADD definitions.json /etc/rabbitmq
ADD rabbitmq.conf /etc/rabbitmq

RUN rabbitmq-plugins enable rabbitmq_shovel
RUN rabbitmq-plugins enable rabbitmq_shovel_management