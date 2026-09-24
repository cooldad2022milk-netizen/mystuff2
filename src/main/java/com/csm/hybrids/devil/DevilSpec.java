package com.csm.hybrids.devil;

import com.csm.hybrids.hybrid.HybridType;
import net.minecraft.world.BossEvent;

/**
 * Everything about one full devil that is not a move: how it fights as a mob (stats, size, boss bar, flight) and how
 * big a player who has become it is.
 * <p>
 * Models are authored at the mob's size; a player's devil form renders the same model scaled down to
 * {@link #playerHeight} so it still fits through the world.
 */
public final class DevilSpec {
    public final HybridType type;

    // ---------------------------------------------------------------- mob
    public double health = 40;
    public double damage = 6;
    public double speed = 0.28;
    public double flySpeed = 0.5;
    public double armor = 4;
    public double toughness = 0;
    public double knockbackResist = 0.3;
    public double followRange = 40;
    public float width = 1f;
    public float height = 2f;
    public int xp = 20;
    /** Multiplier on move damage when the mob uses a move (moves are tuned for players hitting mobs). */
    public float damageScale = 0.4f;
    /** Distance the mob tries to keep from its target between moves. */
    public double preferredRange = 3;
    public float cooldownScale = 1f;
    public boolean flying;
    public boolean stationary;
    public boolean boss;
    public boolean fireImmune;
    public boolean translucent;
    public BossEvent.BossBarColor bar = BossEvent.BossBarColor.RED;
    public float stepHeight = 1f;
    public float shadow = 0.6f;
    /** Spawn egg colours. */
    public int eggBg = 0x222222;
    public int eggFg = 0xAA0000;

    // ---------------------------------------------------------------- playable form
    /** Height of a player in this devil's form (0 = humanoid devil: no model swap, no resize). */
    public float playerHeight;
    public float playerWidth;
    public float playerEye;
    public double formHealth = 10;
    public double formDamage = 4;
    public double formSpeed = 0.1;
    public double formArmor = 4;
    public double formKnockback = 0.3;
    /** Bones hidden in the first-person view of the form (whatever would sit in front of the camera). */
    public String[] firstPersonHidden = {"head"};

    DevilSpec(HybridType type) {
        this.type = type;
    }

    // ---------------------------------------------------------------- builder
    DevilSpec stats(double health, double damage, double speed, double armor) {
        this.health = health;
        this.damage = damage;
        this.speed = speed;
        this.armor = armor;
        return this;
    }

    DevilSpec size(float width, float height) {
        this.width = width;
        this.height = height;
        this.shadow = Math.min(2.5f, width * 0.6f);
        return this;
    }

    DevilSpec fight(float damageScale, double preferredRange, int xp) {
        this.damageScale = damageScale;
        this.preferredRange = preferredRange;
        this.xp = xp;
        return this;
    }

    DevilSpec boss(BossEvent.BossBarColor bar) {
        this.boss = true;
        this.bar = bar;
        this.knockbackResist = Math.max(knockbackResist, 0.8);
        this.followRange = 64;
        return this;
    }

    DevilSpec flying(double flySpeed) {
        this.flying = true;
        this.flySpeed = flySpeed;
        return this;
    }

    DevilSpec stationary() {
        this.stationary = true;
        this.speed = 0;
        this.knockbackResist = 1;
        return this;
    }

    DevilSpec egg(int bg, int fg) {
        this.eggBg = bg;
        this.eggFg = fg;
        return this;
    }

    /** Player form: height (width follows the mob's proportions, capped so doors and tunnels still work). */
    DevilSpec form(float playerHeight, double health, double damage, double speed, double armor) {
        this.playerHeight = playerHeight;
        this.playerWidth = Math.min(1.6f, Math.max(0.6f, width * playerHeight / height));
        this.playerEye = playerHeight * 0.85f;
        this.formHealth = health;
        this.formDamage = damage;
        this.formSpeed = speed;
        this.formArmor = armor;
        return this;
    }

    /** Humanoid devils keep the player's body; only attributes change. */
    DevilSpec humanForm(double health, double damage, double speed, double armor) {
        this.playerHeight = 0;
        this.formHealth = health;
        this.formDamage = damage;
        this.formSpeed = speed;
        this.formArmor = armor;
        return this;
    }

    DevilSpec eye(float fraction) {
        this.playerEye = playerHeight * fraction;
        return this;
    }

    DevilSpec fpHidden(String... bones) {
        this.firstPersonHidden = bones;
        return this;
    }

    DevilSpec translucent() {
        this.translucent = true;
        return this;
    }

    DevilSpec fireImmune() {
        this.fireImmune = true;
        return this;
    }

    // ---------------------------------------------------------------- derived
    public boolean resizesPlayer() {
        return playerHeight > 0;
    }

    /** Model scale when a player wears this form. */
    public float playerScale() {
        return playerHeight > 0 ? playerHeight / height : 1f;
    }
}
