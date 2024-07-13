# Note

Direct message delivery with [_publisher confirms_](https://pika.readthedocs.io/en/stable/examples/blocking_delivery_confirmations.html) pattern.

## Instructions

1. Run `docker compose up --detach --wait`
2. You need two terminals/panes.
I'm using [tmux](https://github.com/tmux/tmux/wiki) to split the terminal into panes.
   <br>
   Run `tmux new-session \; split-window -v \; select-pane -U \;`
3. In the *bottom pane* run `docker compose exec consumer python /usr/src/consumer.py`
4. In the *top pane* run `for i in {1..6}; do docker compose exec producer python /usr/src/producer.py; done`
5. In the *top pane* run `docker compose down --volumes && docker network rm -f rabbitmq`

To access RabbitMQ management console go to [localhost:15672](http://localhost:15672) and use following credentials:
* Username: `bugs`
* Password: `bunny`

## Terminal

![Simple Queue](docs/assets/messaging-simple-queue-timer-small.gif)

## Testing

```bash
bash src/scripts/rabbitmq-e2e-tests.sh
```

## Debug

```bash
docker compose exec broker rabbitmqctl list_queues
docker compose exec broker rabbitmqctl list_bindings
docker compose exec broker rabbitmqctl list_exchanges
```
