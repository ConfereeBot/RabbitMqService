FROM rabbitmq:3-management

# Устанавливаем необходимые утилиты
RUN apt-get update && apt-get install -y wget && rm -rf /var/lib/apt/lists/*
RUN wget -O /plugins/rabbitmq_delayed_message_exchange.ez \
    https://github.com/rabbitmq/rabbitmq-delayed-message-exchange/releases/download/v3.13.0/rabbitmq_delayed_message_exchange-3.13.0.ez
RUN rabbitmq-plugins enable --offline rabbitmq_delayed_message_exchange

COPY definitions.json /etc/rabbitmq/definitions.json

EXPOSE 5672 15672
