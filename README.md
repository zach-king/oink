# Oink

A CLI budgeting tool for nerds. Uses a sqlite3 db stored in the folder of your
choice (hint: Dropbox).

Currently only supports Python 3.x.

## Installation

To install *Oink* simply run the following from the same directory as the `setup.py` file:  

```
python setup.py install
```

Now you can launch *Oink* from anywhere via the command-line with the `oink` command.


## Commands

Type `?` at any time to see the current sections available commands.

`<arg>` style arguments are required.

`[arg]` style arguments are optional.

__Accounts__

- `la` - List all bank accounts and their details.
- `aa` - Add a new bank account.
- `ra` - Rename a bank account.
- `da <id>` - Delete a bank account.

__Transactions__

- `at` - Record a new transaction.
- `lt [account] [num]` - List `[num]` recent transactions for account. Defaults to 10. `lt * *` to list *all* transactions for *all* accounts.
- `ar <amount> <source_account> <destination_account>` - Add transfer transaction between two accounts.
- `et <id>` - Edit a transaction.
- `dt <id>` - Delete a transaction.

__Categories__

- `ac <name>` - Add new category for budgeting and grouping transactions.
- `lc` - List all categories
- `rc <name> <new_name>` - Rename a category
- `dc <id>` - delete a category

__Budgets__
- `ab <account_id>` - Add new budget for an account
- `lb [month] [year]` - List budgets for all accounts. Use `[month]` and `[year]` to filter for specific months.
- `db <id>` - Delete a budget

__Reports__

- `rep <file> <from_date> [to_date] [format]` - Generate a report for a date range. Default is from `<from_date>` to the current date. If no `<format>` is specified, will attempt to infer the format based on the file extension. Date formats are in the YYYY-mm-dd format (e.g. `2018-06-23`).


## TODO
Please be aware this project is still incubating and has not
yet reached a fully stable release. Below are some of
my top-priority tasks (in an arbitrary order albeit) for Oink:

- [ ] Write base unit tests
- [x] Add tab completion to command input
- [ ] Implement CSV report support
- [ ] Implement PDF report support
- [x] Implement JSON report support
- [x] Implement TXT report support
- [ ] Implement MarkDown report support
- [ ] Implement HTML report support
- [ ] Add support for recurring transactions
- [ ] Add new transaction type for transfer transactions
- [ ] Add category-transaction breakdown to reports
- [ ] Add support for Oink to be run as traditional CLI (e.g. `oink <command> <args> [opts]`)
- [ ] Persist command history between sessions
- [ ] Automatic budget renewals per month
- [ ] Automatic report generation per month
- [ ] OS push notifications
