# Instructions

1. Run `docker compose up --detach --wait`
2. You need two terminals/panes.
I'm using [tmux](https://github.com/tmux/tmux/wiki) to split the terminal into panes.
   <br>
   Run `tmux new-session \; split-window -v \; select-pane -U \;`
3. In the **bottom pane** run `docker compose exec server python /usr/src/server.py`
4. In the **top pane** run `for i in {1..6}; do docker compose exec client python /usr/src/client.py; done`
5. In the **top pane** run `docker compose down --volumes && docker network rm -f rabbitmq`

To access RabbitMQ management console go to [localhost:15672](http://localhost:15672) and use following credentials:

* Username: `bugs`
* Password: `bunny`

## Terminal

![Request Response](docs/assets/messaging-request-response-timer.gif)

## Testing

```bash
bash src/scripts/rabbitmq-tests-e2e.sh
docker compose exec producer bash -c "python -m unittest discover /usr/src"
docker compose exec server python -m unittest /usr/src/tests/test_server.py
docker compose exec client python -m unittest /usr/src/tests/test_client.py
```

## Debug

```bash
docker compose exec broker rabbitmqctl list_queues
docker compose exec broker rabbitmqctl list_bindings
docker compose exec broker rabbitmqctl list_exchanges
```