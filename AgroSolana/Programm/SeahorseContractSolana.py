from seahorse.prelude import *

# 1. Уникальный адрес программы
declare_id('Hgsg56L4yXEYharB4iE9CYmUzkHfzp8ogtHNdHhLwNG3')

# 2. ОПРЕДЕЛЕНИЕ СТРУКТУР
class Asset(Account):
    admin: Pubkey
    description: Array[u8, 64]   # ИСПРАВЛЕНО: str[64] → Array[u8, 64]
    total_shares: u64
    price_per_share: u64
    sold_shares: u64
    vault_balance: u64

class ShareHolder(Account):
    owner: Pubkey
    asset: Pubkey
    shares_count: u64
    unclaimed_dividends: u64

# 3. ИНСТРУКЦИИ
@instruction
def init_asset(
    admin: Signer,
    asset: Empty[Asset],
    shares: u64,
    price: u64,
    asset_id: u64
):
    new_asset = asset.init(payer = admin, seeds = ['asset', asset_id])
    new_asset.admin           = admin.key()
    new_asset.total_shares    = shares
    new_asset.price_per_share = price
    new_asset.sold_shares     = 0
    new_asset.vault_balance   = 0

@instruction
def buy_shares(
    user: Signer,
    asset: Asset,
    holder: Empty[ShareHolder],
    admin_account: UncheckedAccount,
    amount: u64
):
    # Проверка наличия долей
    assert asset.sold_shares + amount <= asset.total_shares, 'No shares left'

    # Проверка, что SOL уйдут именно на кошелёк админа этого актива
    assert admin_account.key() == asset.admin, 'Wrong admin account'

    # Расчёт и перевод SOL
    total_cost = amount * asset.price_per_share
    user.transfer_lamports(admin_account, total_cost)

    # Регистрация инвестора
    new_holder = holder.init(payer = user, seeds = ['holder', user.key(), asset.key()])
    new_holder.owner               = user.key()
    new_holder.asset               = asset.key()
    new_holder.shares_count        = amount
    new_holder.unclaimed_dividends = 0

    # Обновление данных в блокчейне
    asset.sold_shares += amount
