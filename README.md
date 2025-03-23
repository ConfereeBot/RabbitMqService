# RabbitMqService
A message broker for binding ConfereeTgBot and GMeetBot.

## Schema
```mermaid
graph LR
    subgraph VHost["/"]
        direction LR
        conferee_direct["conferee_direct (exchange)"]
        gmeet_manage["gmeet_manage (queue)"]
        gmeet_res["gmeet_res (queue)"]
        gmeet_schedule["gmeet_schedule (queue)"]
        gmeet_tasks["gmeet_tasks (queue)"]
    end

    conferee_direct -->|routing_key: gmeet_manage| gmeet_manage
    conferee_direct -->|routing_key: gmeet_res| gmeet_res
    conferee_direct -->|routing_key: gmeet_schedule| gmeet_schedule
    conferee_direct -->|routing_key: gmeet_tasks| gmeet_tasks

    gmeet_schedule -.->|x-dead-letter-routing-key: gmeet_tasks| gmeet_tasks
    gmeet_tasks -.->|x-dead-letter-routing-key: gmeet_res| gmeet_res
    gmeet_manage -.->|x-dead-letter-routing-key: gmeet_res| gmeet_res
```

## Service deployment
1. Clone `https://github.com/ConfereeBot/RabbitMqService.git`
2. Start container `docker compose up -d --build`
3. Load definitions **once** `docker exec rabbitmq rabbitmqctl import_definitions /etc/rabbitmq/definitions.json`
4. [Log in](http://localhost:15672/) with
- login: `guest`
- password: `guest`
