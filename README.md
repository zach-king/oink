# Oink

A CLI budgeting tool for nerds. Uses a sqlite3 db stored in the folder of your
choice (hint: Dropbox).

 
 ## Sections

These are the general "sections" of the tool that are available to you. Each
have their own set of commands.

- Accounts: Manage bank accounts
- Budget: View and manage budget categories
- Transactions: View and manage transactions
- Reports: Generate budget and transaction reports


## Commands

Type `?` at any time to see the current sections available commands.

- [global] - Can be called anywhere
    - `ls accounts` - Same as `accounts` -> `list`
    - `ls budget` - Same as `budget` -> `list`
    - `ls transactions` - Same as `transactions` -> `list`
- `accounts` - Go to account section
    - `ls` (Default) - View, lists account names and balances
    - `add` - Creat a new account
    - `edit <account>` - Edit account details
    - `del <account>` - Delete account
- `budget` - Go to budget section
    - `ls` (Default) - View budget details and percents for current month
    - `ls <int:month>` - View budget details for given month (numeric)
    - `add` - Add a new budget category
    - `set <category> <float:amount>` - Set budget category amount for current month
    - `edit <category>` - Edit category name
    - `del <category>` - Delete category
- `transactions` - Go to transactions section
    - `ls` (Default) - View last 10 transactions
    - `ls <int:num>` - View last X transactions
    - `filter` - Filter transactions by account
    - `add` - Add new transaction to account. Should have an easy way to add another transaction to the same account
    - `transfer` - Add a transfer transaction between two accounts
    - `edit <transaction_id>` - Edit transaction or transfer
    - `del <transaction_id>` - Delete transaction or transfer
    - `confirm` - Start confirming unconfirmed transactions
- `reports` - Go to reports section
    - TODO