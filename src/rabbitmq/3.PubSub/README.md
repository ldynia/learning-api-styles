# Instructions

1. Run `docker compose up --detach --wait`
2. You need three terminals/panes.
I'm using [tmux](https://github.com/tmux/tmux/wiki) to split the terminal into panes.
   <br>
   Run `tmux new-session \; split-window -v \; split-window -h \; select-pane -U \;`
3. In the **bottom left pane** run `docker compose exec consumer-a python /usr/src/consumer.py`
4. In the **bottom right pane** run `docker compose exec consumer-b python /usr/src/consumer.py`
5. In the **top pane** run `for i in {1..6}; do docker compose exec producer python /usr/src/producer.py; done`
6. In the **top pane** run `docker compose down --volumes && docker network rm -f rabbitmq`

To access RabbitMQ management console go to [localhost:15672](http://localhost:15672) and use following credentials:

* Username: `bugs`
* Password: `bunny`

## Terminal

![PubSub](docs/assets/messaging-pub-sub-timer.gif)

## Testing

```bash
bash src/scripts/rabbitmq-tests-e2e.sh
docker compose exec producer bash -c "python -m unittest discover /usr/src"
docker compose exec producer python -m unittest /usr/src/tests/test_producer.py
docker compose exec consumer-a python -m unittest /usr/src/tests/test_consumer.py
```

## Debug

```bash
docker compose exec broker rabbitmqctl list_queues
docker compose exec broker rabbitmqctl list_bindings
docker compose exec broker rabbitmqctl list_exchanges
```