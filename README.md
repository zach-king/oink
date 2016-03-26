# Oink

A CLI budgeting tool for nerds. Uses a sqlite3 db stored in the folder of your
choice (hint: Dropbox).

Currently only supports Python 3.x. I plan to add support for 2.7 after initial
concept is complete.

 
## Commands

Type `?` at any time to see the current sections available commands.

__Accounts__

- `ls accounts` - List all bank accounts and their details.
- `add account` - Add a new bank account.
- `edit account <name>` - Edit a bank account.
- `del account <name>` - Delete a bank account.

__Budget__

- `ls budget [mm] [yyyy]` - List all budget categories for a month. Defaults to current month.
- `add budget` - Add new budget category.
- `set budget <category> <amount>` - Set budget category amount for the current month.
- `edit budget <category>` - Change budget category name.
- `del budget <category>` - Delete budget category.

__Transactions__

- `ls trans [num]` - List [num] recent transactions from all accounts. Defaults to 10.
- `ls trans <account> [num]` - List [num] recent transactions for account. Defaults to 10.
- `add trans` - Add a new transaction.
- `transfer` - Add transfer transaction between two accounts.
- `edit trans <id>` - Edit a transaction.
- `del trans <id>` - Delete a transaction.

__Reports__

TODO