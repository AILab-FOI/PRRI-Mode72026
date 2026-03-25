# Issue #2 Report: Igrac mehanike

Ovaj report opisuje sto je mijenjano za issue `#2`:

- kretanje
- pucanje
- hitbox
- i-frames
- power-up primanje

Sve je pisano laicki, s kratkim snippetima iz koda.

## 1. Kretanje je manje "digitalno", a vise kao letjelica

Prije se igrac odmah pomicao punom brzinom u bilo kojem smjeru. To je radilo, ali je djelovalo grubo i dijagonala je bila prejaka.

Sada igrac ima malu inerciju:

```python
input_length = np.linalg.norm(move_input)
if input_length > 0:
    move_input /= input_length
    desired_velocity = (
        forward * move_input[1] + right * move_input[0]
    ) * self.base_speed * self.speed_multiplier
    self.velocity += (desired_velocity - self.velocity) * self.acceleration
else:
    self.velocity *= self.drag
```

Sto to znaci u igri:

- dijagonalno kretanje vise nije brze od ravnog
- letjelica ne "trza", nego lagano ulazi i izlazi iz kretanja
- upravljanje i dalje ostaje jednostavno, bez velikog physics sustava

## 2. I-frames sprjecavaju nepravedan chain damage

Prije je igrac mogao dobiti vise hitova skoro u istom trenutku. To je bilo posebno neugodno kad se metak i enemy kontakt dogode zajedno.

Sada nakon primljenog udarca postoji kratki zastitni prozor:

```python
def take_damage(self, amount):
    now = time.time()
    if now < self.invulnerable_until or self.health <= 0:
        return False

    self.health = max(0, self.health - amount)
    self.invulnerable_until = now + self.invulnerability_duration
    self.hit_sound.play()
    return True
```

Sto to znaci u igri:

- jedan pogodak vise ne moze odmah pretvoriti u 2-3 uzastopna
- igrac dobije kratki trenutak za oporavak i reakciju
- health UI kratko blinka kao znak da je zastita aktivna

## 3. Hitboxovi su precizniji po tipu neprijatelja i projektila

Prije su kolizije koristile gotovo fiksne udaljenosti. To je bilo brzo za implementirati, ali nije bilo jednako fer za sve vrste enemya.

Sada svaki tip ima svoje radijuse:

```python
self.hit_radius = 0.55
self.contact_radius = 0.42
self.bullet_hit_radius = 0.18
```

Primjer za tezi enemy:

```python
self.hit_radius = 0.72
self.contact_radius = 0.5
self.bullet_hit_radius = 0.22
```

I provjera kolizije je sada jasnija:

```python
if np.linalg.norm(self.pos - projectile.pos) < self.hit_radius + projectile.hit_radius:
    ...
```

Sto to znaci u igri:

- tank enemy je stvarno "veca meta"
- mali enemy nije nepravedno sirok
- sudari igraca, enemyja i metaka su konzistentniji

## 4. Pucanje ima bolji ritam i vise karaktera

Prije je razlika medu oruzjima bila relativno mala u osjecaju. Sada svako ima svoj ritam pucanja i malo drukciji spread.

Cooldowni po oruzju:

```python
self.weapon_cooldowns = {
    WeaponType.REVOLVER: 0.34,
    WeaponType.SHOTGUN: 0.58,
    WeaponType.MINIGUN: 0.09,
}
```

Provjera pucanja:

```python
def can_fire_weapon(self):
    cooldown = self.weapon_cooldowns[self.weapon]
    return time.time() - self.last_shot_time >= cooldown
```

Mali spread za vise "ziv" osjecaj:

```python
spread = random.uniform(-0.06, 0.06)
self.projectiles.append(Projectile(pos, angle + spread, speed=0.54, offset_distance=offset))
```

Sto to znaci u igri:

- revolver ima cist, ritmican shot
- shotgun djeluje siroko i tesko
- minigun vise ne puca kao "isti space spam", nego kao stabilan stream
- svaki weapon sada koristi prikladniji zvuk

## 5. Pogodak na enemyju sada je citljiviji

U kodu je vec postojao `hit_timer`, ali nije davao dovoljno vizualne koristi. Sad se koristi za kratki flash prsten oko neprijatelja:

```python
if self.hit_timer > 0:
    pg.draw.circle(
        screen,
        (255, 226, 128),
        (int(screen_x), int(screen_y)),
        max(6, scale // 2 + 6),
        flash_width,
    )
```

Sto to znaci u igri:

- igrac odmah vidi da je hit registriran
- borba je citljivija i "socnija"

## 6. Power-up primanje je mekse i jasnije

Prije je pickup radio po principu: dotaknes item i on odmah nestane. Sada pickupovi imaju magnet efekt, lagano plutaju i ostaju na mapi ako health pickup ne moze nista izliječiti.

Magnet efekt:

```python
if 0 < distance < self.magnet_radius:
    direction = (player_pos - self.pos) / distance
    self.pos += direction * min(self.magnet_speed, distance)
```

Health pickup se vise ne trosi uzalud:

```python
if self.player.health < self.player.max_health:
    self.player.health += 5
    ...
    return True
return False
```

Status poruka za pickup:

```python
def show_status_message(self, message, duration=1.8):
    self.status_message = message
    self.status_message_until = time.time() + duration
```

Sto to znaci u igri:

- power-upovi "prilaze" igracu pa je skupljanje ugodnije
- health pickup ne propada kad si na full healthu
- igrac dobije jasan tekstualni feedback kad pokupi boost ili oruzje

## 7. Kako su promjene razlomljene po commitima

Promjene su namjerno podijeljene u vise manjih commitova:

1. `feat: smooth player movement and add i-frames (#2)`
2. `feat: improve weapon cadence and hit feedback (#2)`
3. `feat: polish pickups and combat HUD cues (#2)`
4. `docs: add issue #2 gameplay change report (#2)`

To olaksava review jer se svaka cjelina moze gledati zasebno.
