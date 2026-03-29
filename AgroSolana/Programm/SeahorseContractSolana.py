from seahorse.prelude import *

declare_id('AgroShare1111111111111111111111111111111')

# Состояние актива (трактор, комбайн и т.д.)
class Asset(Account):
    admin: Pubkey
    description: str[64]
    total_shares: u64
    price_per_share: u64
    sold_shares: u64
    vault_balance: u64  # Накопленные дивиденды для выплаты

# Состояние инвестора
class ShareHolder(Account):
    owner: Pubkey
    asset: Pubkey
    shares_count: u64
    unclaimed_dividends: u64 # Причитающаяся прибыль

@instruction
def init_asset(admin: Signer, asset: Empty[Asset], desc: str[64], shares: u64, price: u64):
    # Создание записи об активе
    new_asset = asset.init(payer = admin, seeds = ['v1', desc])
    new_asset.admin = admin.key()
    new_asset.description = desc
    new_asset.total_shares = shares
    new_asset.price_per_share = price
    new_asset.sold_shares = 0
    new_asset.vault_balance = 0

@instruction
def buy_shares(user: Signer, asset: Asset, holder: Empty[ShareHolder], amount: u64):
    # 1. Проверки
    assert asset.sold_shares + amount <= asset.total_shares, 'Превышен лимит долей'
    
    # 2. Расчет стоимости
    total_cost = amount * asset.price_per_share
    
    # 3. РЕАЛЬНЫЙ ПЕРЕВОД ДЕНЕГ (SOL)
    # Переводим SOL от покупателя на аккаунт администратора актива
    user.transfer_lamports(asset.admin, total_cost)
    
    # 4. Регистрация владельца
    new_holder = holder.init(payer = user, seeds = [user, asset.key()])
    new_holder.owner = user.key()
    new_holder.asset = asset.key()
    new_holder.shares_count = amount
    new_holder.unclaimed_dividends = 0
    
    # 5. Обновление данных актива
    asset.sold_shares += amount

@instruction
def add_profit(admin: Signer, asset: Asset, total_profit: u64):
    # Функция для начисления прибыли (например, от аренды трактора)
    # Только админ может вызвать эту функцию
    assert admin.key() == asset.admin, 'Доступ запрещен'
    
    # Переводим прибыль от админа на "баланс" контракта
    admin.transfer_lamports(asset, total_profit)
    asset.vault_balance += total_profit
    # В реальном коде здесь была бы логика распределения на каждого holder'а

@instruction
def claim_dividends(user: Signer, asset: Asset, holder: ShareHolder):
    # Инвестор забирает свою часть прибыли
    assert holder.owner == user.key(), 'Это не ваш аккаунт'
    
    # Пример логики: выплачиваем фиксированную часть из vault_balance
    payout = holder.unclaimed_dividends
    assert payout > 0, 'Нет доступных выплат'
    
    # Перевод SOL обратно пользователю
    asset.transfer_lamports(user, payout)
    holder.unclaimed_dividends = 0