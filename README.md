# Oink

A CLI budgeting tool for nerds. Uses a sqlite3 db stored in the folder of your
choice (hint: Dropbox).

Currently only supports Python 3.x. I plan to add support for 2.7 after initial
concept is complete.

 
## Commands

Type `?` at any time to see the current sections available commands.

`<arg>` style arguments are required.

`[arg]` style arguments are optional.

__Accounts__

- `la` - List all bank accounts and their details.
- `aa` - Add a new bank account.
- `da <name>` - Delete a bank account.

__Budget__

- `ab` - Add new budget category.
- `lb [mm] [yyyy]` - List all budget categories for a month. Defaults to current month.
- `sb <category> <amount>` - Set budget category amount for the current month.
- `rb <oldname> <newname>` - Change budget category name.
- `db <category>` - Delete budget category.

__Transactions__

- `lt [account] [num]` - List [num] recent transactions for account. Defaults to 10.
- `at` - Record a new transaction.
- `ar [source] [dest] [amount]` - Add transfer transaction between two accounts.
- `et <id>` - Edit a transaction.
- `dt <id>` - Delete a transaction.

__Reports__

- `rep <account> <file> [format]` - Generate a report in the specified format, and save it to a file. Currently only supports TXT. Formats CSV, HTML, and PDF coming very soon.


## TODO

- Write unit tests for budget
- Write unit tests for transactions
- Add tab completion to command input
- Implement CSV report generation
- Implement HTML report generation
- Implement PDF report generation
- Refactor budget table to have a PK of (name, account, month) to support same-name categories for different accounts
