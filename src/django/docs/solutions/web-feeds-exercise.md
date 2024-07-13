# Exercise 3

Your task is to read an Atom feed from the *`forecast/feed`* endpoint implemented in this chapter. You are given provisioned for this book github codespace that contains RSS/Atom CLI reader called [newsboat](https://newsboat.org/). To complete this exercise, you'll need to start the Django project with the command *`docker compose up`*, change the codespace's port visibility, and configure the newsboat reader to read the feeds from the project's codespaces URL. This exercise requires changing the codespace's URL visibility to the public. To do so, in the codespaces *`PORTS`* tab, right-click on port *`8000`*, and from the menu *`Port Visibility`* choose *`Public`*.

## Solution

1. Start the Django project. This step will take several minutes to complete.
    ```bash
    cd src/django
    docker compose up --detach --wait
    ```

2. Change port visibility and get the application URL.

    * Go to codespaces *`PORTS`* tab.
    * Right-click on port *`8000`*.
    * From the menu *`Port Visibility`* choose *`Public`*.
    * Again right-click on port *`8000`* and choose *`Copy Local Address`*.

3. Configure and run *`newsboat`*.

    ```bash
    # !!! Change codespace-url to copied URL from the above (Copy Local Address step) !!!
    echo "https://codespace-url/forecast/feed" > /home/vscode/.newsboat/urls

    # Press `r` or `R` to reload feed.
    newsboat
    ```