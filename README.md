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

TODO

- `sb <category> <amount>` - Set budget category amount for the current month.
- `eb <category>` - Change budget category name.
- `db <category>` - Delete budget category.

__Transactions__

- `lt [account] [num]` - List [num] recent transactions for account. Defaults to 10.
- `at` - Record a new transaction.
- `ar [source] [dest] [amount]` - Add transfer transaction between two accounts.
- `dt <id>` - Delete a transaction.

TODO

- `et <id>` - Edit a transaction.

__Reports__

TODO

- `rep <account> <format> <file>` - Generate a report in the specified format, and save it to a file. Should support formats CSV and PDF.


## TODO

- Write unit tests for budget
- Write unit tests for transactions
- Add color to output
- Add tab completion to command input
- Sort output of commands in their own headers when printing help (should look similar to README)
- Refactor commands with the optional argument support
- Should `dt` on a transfer automatically delete *both* transactions?
