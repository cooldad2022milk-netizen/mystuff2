package com.csm.hybrids.ability.devil;

import com.csm.hybrids.ability.Ability;
import com.csm.hybrids.ability.AbilityRun;
import com.csm.hybrids.ability.AbilityUtil;
import com.csm.hybrids.entity.devil.DevilEntity;
import com.csm.hybrids.fx.Fx;
import com.csm.hybrids.hybrid.HybridType;
import com.csm.hybrids.registry.ModSounds;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.effect.MobEffectInstance;
import net.minecraft.world.effect.MobEffects;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.Mob;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.phys.Vec3;

import java.util.List;

/** The devils who look like people: the Angel Devil, Yoru (the War Devil) and Fami (the Famine Devil). */
public final class HumanDevilMoves {
    /** Years of life the Angel has taken and not yet forged into weapons. */
    public static final String LIFESPAN = "csm_lifespan";
    /** Yoru's last weapon: the next few blows land harder. */
    public static final String WEAPON = "csm_war_weapon";
    public static final String STARVED_UNTIL = "csm_starved_until";

    public static List<Ability> angel() {
        return List.of(new LifespanDrain(), new LifespanSword(), new LifespanSpears(), new WingBeat());
    }

    public static List<Ability> war() {
        return List.of(new Weaponize(), new UniformSword(), new SpearThrow(), new Arsenal());
    }

    public static List<Ability> famine() {
        return List.of(new Starve(), new Enthrall(), new Vanish(), new Feast());
    }

    static int lifespan(LivingEntity u) {
        return u.getPersistentData().getInt(LIFESPAN);
    }

    static void addLifespan(LivingEntity u, int n) {
        CompoundTag t = u.getPersistentData();
        t.putInt(LIFESPAN, Math.max(0, Math.min(6, t.getInt(LIFESPAN) + n)));
        if (u instanceof ServerPlayer sp) {
            sp.displayClientMessage(Component.translatable("msg.csm.lifespan", t.getInt(LIFESPAN)), true);
        }
    }

    /** Spends up to {@code max} stolen years; the mob Angel always has some to spend. */
    static int spendLifespan(LivingEntity u, int max) {
        if (!(u instanceof Player)) {
            return max;
        }
        int have = lifespan(u);
        int used = Math.min(have, max);
        u.getPersistentData().putInt(LIFESPAN, have - used);
        return used;
    }

    static int weaponCharges(LivingEntity u) {
        return u.getPersistentData().getInt(WEAPON);
    }

    static boolean useWeaponCharge(LivingEntity u) {
        int n = weaponCharges(u);
        if (n <= 0) {
            return false;
        }
        u.getPersistentData().putInt(WEAPON, n - 1);
        return true;
    }

    // ================================================================== Angel Devil
    /** Whatever he touches loses years of its life - and he keeps them. */
    public static class LifespanDrain extends DevilAbility {
        public LifespanDrain() {
            super(HybridType.ANGEL, "angel_touch");
            anyForm();
            timing(18, 60);
            cost(4);
            anim("angel_touch", "touch");
            ai(0, 3, 12);
            reach(5);
        }

        @Override
        public void perform(LivingEntity user, AbilityRun run) {
            if (run.tick != 6) {
                return;
            }
            ServerLevel level = level(user);
            for (LivingEntity e : coneTargets(user, run, user.getEyePosition(), AbilityUtil.aim(user),
                    2.8 + user.getBbWidth() * 0.5, 50)) {
                AbilityUtil.hurtIgnoringIFrames(user, e, 7f);
                e.addEffect(AbilityUtil.quiet(new MobEffectInstance(MobEffects.WITHER, 100, 1)));
                e.addEffect(AbilityUtil.quiet(new MobEffectInstance(MobEffects.WEAKNESS, 200, 1)));
                e.addEffect(AbilityUtil.quiet(new MobEffectInstance(MobEffects.MOVEMENT_SLOWDOWN, 100, 1)));
                user.heal(4f);
                addLifespan(user, 2);
                Vec3 c = e.getBoundingBox().getCenter();
                Fx.stars(level, c, 10, 0.4);
                Fx.speedLine(level, c, AbilityUtil.handPos(user, true, 0.6));
                AbilityUtil.sound(user, ModSounds.BLOOD_DRINK.get(), 1.0f, 1.5f);
                break;
            }
        }
    }

    /** A golden sword forged out of stolen years: one long diagonal cut. */
    public static class LifespanSword extends DevilAbility {
        public LifespanSword() {
            super(HybridType.ANGEL, "angel_sword");
            timing(20, 40);
            cost(6);
            anim("angel_sword", "sword");
            fx("sword");
            ai(0, 4, 14);
        }

        @Override
        public void perform(LivingEntity user, AbilityRun run) {
            ServerLevel level = level(user);
            if (run.tick == 2) {
                run.counter = spendLifespan(user, 1);
                AbilityUtil.sound(user, ModSounds.KATANA_DRAW.get(), 1.0f, 1.3f);
            }
            if (run.tick != 10) {
                return;
            }
            Vec3 aim = AbilityUtil.aim(user);
            AbilityUtil.sound(user, ModSounds.KATANA_SLASH.get(), 1.4f, 0.9f);
            Fx.slash(level, user.getEyePosition().add(aim.scale(2.4)), aim.cross(new Vec3(0, 1, 0)).add(0, 0.8, 0), 3.0);
            float dmg = 13f + run.counter * 8f;
            for (LivingEntity e : coneTargets(user, run, user.getEyePosition(), aim, 4.2 + user.getBbWidth() * 0.5, 70)) {
                AbilityUtil.hurtIgnoringIFrames(user, e, dmg);
                AbilityUtil.blood(level, e.getBoundingBox().getCenter(), 30, 0.4);
                Fx.stars(level, e.getBoundingBox().getCenter(), 4, 0.3);
            }
        }
    }

    /** He raises a hand and his stolen years fall from the sky as spears. */
    public static class LifespanSpears extends DevilAbility {
        public LifespanSpears() {
            super(HybridType.ANGEL, "angel_spears");
            timing(30, 160);
            cost(12);
            anim("angel_spears", "spears");
            fx("spears");
            ai(2, 24, 9);
            reach(32);
        }

        @Override
        public void perform(LivingEntity user, AbilityRun run) {
            ServerLevel level = level(user);
            if (run.tick == 4) {
                LivingEntity t = target(run);
                run.vec = t != null ? t.position() : AbilityUtil.raycastBlock(user, reach).getLocation();
                run.counter = 6 + 2 * spendLifespan(user, 3);
                AbilityUtil.sound(user, ModSounds.COSMOS_HALLOWEEN.get(), 0.9f, 1.8f);
            }
            if (run.vec == null || run.tick < 18 || run.tick > 28) {
                return;
            }
            int per = Math.max(1, run.counter / 6);
            for (int i = 0; i < per; i++) {
                double a = level.random.nextDouble() * Math.PI * 2;
                double r = level.random.nextDouble() * 3.5;
                Vec3 p = AbilityUtil.groundBelow(level, run.vec.add(Math.cos(a) * r, 3, Math.sin(a) * r), 8);
                Fx.speedLine(level, p.add(0, 14, 0), p);
                Fx.impact(level, p, 0.7);
                Fx.stars(level, p.add(0, 0.3, 0), 4, 0.3);
                AbilityUtil.soundAt(level, p, ModSounds.SPEAR_IMPACT.get(), 0.9f, 1.4f);
                for (LivingEntity e : AbilityUtil.inRadius(user, p, 1.4)) {
                    AbilityUtil.hurtIgnoringIFrames(user, e, 7f);
                    AbilityUtil.blood(level, e.getBoundingBox().getCenter(), 16, 0.3);
                }
            }
        }
    }

    /** One hard beat of the wings: everything in front is blown away and he is carried up and back. */
    public static class WingBeat extends DevilAbility {
        public WingBeat() {
            super(HybridType.ANGEL, "angel_gust");
            timing(16, 80);
            cost(6);
            anim("angel_gust", "gust");
            ai(0, 6, 8);
            mobile();
        }

        @Override
        public void perform(LivingEntity user, AbilityRun run) {
            if (run.tick != 4) {
                return;
            }
            ServerLevel level = level(user);
            Vec3 aim = AbilityUtil.aim(user);
            AbilityUtil.sound(user, ModSounds.DEVIL_FLAP.get(), 1.6f, 1.2f);
            AbilityUtil.sound(user, ModSounds.DEVIL_GUST.get(), 1.0f, 1.4f);
            for (int k = 0; k < 6; k++) {
                Vec3 side = aim.cross(new Vec3(0, 1, 0)).normalize().scale((k - 2.5) * 0.6);
                Vec3 from = user.getEyePosition().add(side).add(aim.scale(0.5));
                Fx.speedLine(level, from, from.add(aim.scale(6)));
            }
            for (LivingEntity e : coneTargets(user, run, user.getEyePosition(), aim, 7, 60)) {
                AbilityUtil.hurtIgnoringIFrames(user, e, 4f);
                AbilityUtil.push(e, user.position(), 2.0, 0.5);
            }
            user.setDeltaMovement(user.getDeltaMovement().add(aim.x * -0.5, 0.8, aim.z * -0.5));
            user.hurtMarked = true;
            user.fallDistance = 0;
        }
    }

    // ================================================================== War Devil (Yoru)
    /** "I'll make you into a weapon." Something weak enough becomes one - and the next blows land harder. */
    public static class Weaponize extends DevilAbility {
        public Weaponize() {
            super(HybridType.WAR, "war_weaponize");
            timing(24, 200);
            cost(10);
            anim("war_weaponize", "weaponize");
            ai(0, 3, 8);
            reach(5);
        }

        @Override
        public void perform(LivingEntity user, AbilityRun run) {
            if (run.tick != 10) {
                return;
            }
            ServerLevel level = level(user);
            for (LivingEntity e : coneTargets(user, run, user.getEyePosition(), AbilityUtil.aim(user),
                    2.8 + user.getBbWidth() * 0.5, 50)) {
                Vec3 c = e.getBoundingBox().getCenter();
                boolean boss = e instanceof DevilEntity d && d.spec().boss;
                boolean weak = e.getHealth() <= Math.max(20f, e.getMaxHealth() * 0.3f);
                AbilityUtil.sound(user, ModSounds.LONGSWORD_CLANG.get(), 1.4f, 0.7f);
                if (weak && !boss && !(e instanceof Player)) {
                    // it folds, twists and hardens into a blade in her hand
                    e.invulnerableTime = 0;
                    e.hurt(AbilityUtil.source(user), Math.max(e.getHealth() + 10f, 40f));
                    AbilityUtil.blood(level, c, 80, 0.5);
                    Fx.gore(level, c, 5);
                    Fx.shards(level, c, 20, 0.3);
                    user.getPersistentData().putInt(WEAPON, 3);
                    user.addEffect(AbilityUtil.quiet(new MobEffectInstance(MobEffects.DAMAGE_BOOST, 600, 1)));
                    if (user instanceof ServerPlayer sp) {
                        sp.displayClientMessage(Component.translatable("msg.csm.weaponized"), true);
                    }
                } else {
                    AbilityUtil.hurtIgnoringIFrames(user, e, 10f);
                    e.addEffect(AbilityUtil.quiet(new MobEffectInstance(MobEffects.WEAKNESS, 160, 1)));
                    Fx.shards(level, c, 8, 0.2);
                    AbilityUtil.blood(level, c, 20, 0.3);
                }
                break;
            }
        }
    }

    /** A crude blade made out of a school uniform: a heavy cut. */
    public static class UniformSword extends DevilAbility {
        public UniformSword() {
            super(HybridType.WAR, "war_sword");
            timing(18, 30);
            cost(4);
            anim("war_sword", "sword");
            fx("sword");
            ai(0, 4, 14);
        }

        @Override
        public void perform(LivingEntity user, AbilityRun run) {
            if (run.tick != 8) {
                return;
            }
            ServerLevel level = level(user);
            Vec3 aim = AbilityUtil.aim(user);
            boolean charged = useWeaponCharge(user);
            AbilityUtil.sound(user, ModSounds.LONGSWORD_CLEAVE.get(), 1.3f, charged ? 0.8f : 1.1f);
            Fx.slash(level, user.getEyePosition().add(aim.scale(2.2)), aim.cross(new Vec3(0, 1, 0)).add(0, -0.4, 0),
                    charged ? 3.2 : 2.4);
            for (LivingEntity e : coneTargets(user, run, user.getEyePosition(), aim, 4.0 + user.getBbWidth() * 0.5, 75)) {
                AbilityUtil.hurtIgnoringIFrames(user, e, charged ? 22f : 14f);
                AbilityUtil.push(e, user.position(), 0.6, 0.2);
                AbilityUtil.blood(level, e.getBoundingBox().getCenter(), 30, 0.4);
            }
        }
    }

    /** A spear hurled with everything she has: it runs through everything in a line. */
    public static class SpearThrow extends DevilAbility {
        public SpearThrow() {
            super(HybridType.WAR, "war_spear");
            timing(22, 90);
            cost(8);
            anim("war_spear", "spear");
            fx("spear");
            ai(4, 28, 10);
            reach(40);
        }

        @Override
        public void perform(LivingEntity user, AbilityRun run) {
            ServerLevel level = level(user);
            if (run.tick == 4) {
                AbilityUtil.sound(user, ModSounds.SPEAR_PULL.get(), 1.0f, 1.0f);
            }
            if (run.tick != 11) {
                return;
            }
            LivingEntity t = target(run);
            Vec3 from = AbilityUtil.handPos(user, true, 0.8);
            Vec3 dir = t != null ? t.getBoundingBox().getCenter().subtract(from).normalize() : AbilityUtil.aim(user);
            Vec3 end = from.add(dir.scale(32));
            net.minecraft.world.phys.BlockHitResult wall = level.clip(new net.minecraft.world.level.ClipContext(from, end,
                    net.minecraft.world.level.ClipContext.Block.COLLIDER, net.minecraft.world.level.ClipContext.Fluid.NONE,
                    user));
            Vec3 limit = wall.getLocation();
            AbilityUtil.sound(user, ModSounds.SPEAR_THROW.get(), 1.4f, 0.9f);
            Fx.speedLine(level, from, limit);
            Fx.impact(level, limit, 1.2);
            AbilityUtil.soundAt(level, limit, ModSounds.SPEAR_IMPACT.get(), 1.4f, 0.8f);
            boolean charged = useWeaponCharge(user);
            for (LivingEntity e : AbilityUtil.alongLine(user, from, limit, 0.6)) {
                AbilityUtil.hurtIgnoringIFrames(user, e, charged ? 26f : 18f);
                AbilityUtil.push(e, from, 0.8, 0.2);
                AbilityUtil.blood(level, e.getBoundingBox().getCenter(), 30, 0.4);
            }
        }
    }

    /** Everything that has ever been a weapon, all at once: a barrage falls round her target. */
    public static class Arsenal extends DevilAbility {
        public Arsenal() {
            super(HybridType.WAR, "war_arsenal");
            timing(50, 300);
            cost(18);
            anim("war_arsenal", "arsenal");
            ai(3, 30, 6);
            reach(40);
        }

        @Override
        public void perform(LivingEntity user, AbilityRun run) {
            ServerLevel level = level(user);
            if (run.tick == 6) {
                LivingEntity t = target(run);
                run.vec = t != null ? t.position() : AbilityUtil.raycastBlock(user, reach).getLocation();
                AbilityUtil.sound(user, ModSounds.DEVIL_ROAR.get(), 1.0f, 1.4f);
            }
            if (run.vec == null || run.tick < 14 || run.tick > 44 || run.tick % 3 != 0) {
                return;
            }
            LivingEntity t = target(run);
            Vec3 centre = t != null ? t.position() : run.vec;
            double a = level.random.nextDouble() * Math.PI * 2;
            double r = level.random.nextDouble() * 3.0;
            Vec3 p = AbilityUtil.groundBelow(level, centre.add(Math.cos(a) * r, 4, Math.sin(a) * r), 10);
            Vec3 sky = p.add(-8 + level.random.nextDouble() * 16, 18, -8 + level.random.nextDouble() * 16);
            Fx.speedLine(level, sky, p);
            Fx.explosion(level, p, 1.4);
            AbilityUtil.soundAt(level, p, ModSounds.BOMB_BLAST.get(), 1.2f, 1.1f);
            for (LivingEntity e : AbilityUtil.inRadius(user, p, 2.2)) {
                AbilityUtil.hurtIgnoringIFrames(user, e, 7f);
                AbilityUtil.push(e, p, 0.6, 0.4);
            }
        }
    }

    // ================================================================== Famine Devil (Fami)
    /** Everything she looks at is suddenly, desperately hungry. */
    public static class Starve extends DevilAbility {
        public Starve() {
            super(HybridType.FAMINE, "famine_starve");
            anyForm();
            timing(20, 120);
            cost(8);
            anim("famine_starve", "starve");
            ai(0, 16, 10);
            reach(20);
        }

        @Override
        public void perform(LivingEntity user, AbilityRun run) {
            if (run.tick != 8) {
                return;
            }
            ServerLevel level = level(user);
            AbilityUtil.sound(user, ModSounds.DEVIL_GROWL.get(), 0.8f, 1.7f);
            for (LivingEntity e : coneTargets(user, run, user.getEyePosition(), AbilityUtil.aim(user), 16, 25)) {
                e.getPersistentData().putLong(STARVED_UNTIL, level.getGameTime() + 300);
                if (e instanceof Player p) {
                    p.getFoodData().setFoodLevel(Math.max(0, p.getFoodData().getFoodLevel() - 8));
                    p.getFoodData().setSaturation(0);
                    p.addEffect(AbilityUtil.quiet(new MobEffectInstance(MobEffects.HUNGER, 300, 2)));
                }
                e.addEffect(AbilityUtil.quiet(new MobEffectInstance(MobEffects.WEAKNESS, 300, 1)));
                e.addEffect(AbilityUtil.quiet(new MobEffectInstance(MobEffects.MOVEMENT_SLOWDOWN, 160, 1)));
                AbilityUtil.hurtIgnoringIFrames(user, e, 6f);
                Fx.smoke(level, e.getEyePosition(), 6, 0.3);
            }
        }
    }

    /** The starving will do anything for her: they turn on whatever she is fighting. */
    public static class Enthrall extends DevilAbility {
        public Enthrall() {
            super(HybridType.FAMINE, "famine_enthrall");
            timing(30, 400);
            cost(16);
            anim("famine_enthrall", "enthrall");
            ai(0, 20, 7);
            blind();
        }

        @Override
        public void perform(LivingEntity user, AbilityRun run) {
            ServerLevel level = level(user);
            if (run.tick == 6) {
                AbilityUtil.sound(user, ModSounds.CONTROL_DOMINATE.get(), 1.2f, 1.3f);
            }
            if (run.tick != 16) {
                return;
            }
            Fx.shockwave(level, user.position(), 14, Fx.BLOOD_RING);
            int taken = 0;
            List<LivingEntity> around = AbilityUtil.inRadius(user, user.position(), 14);
            around.sort(java.util.Comparator.comparingDouble(e -> e.getHealth() / e.getMaxHealth()));
            for (LivingEntity e : around) {
                if (e instanceof Player p) {
                    p.addEffect(AbilityUtil.quiet(new MobEffectInstance(MobEffects.CONFUSION, 160, 0)));
                    p.addEffect(AbilityUtil.quiet(new MobEffectInstance(MobEffects.HUNGER, 200, 1)));
                    continue;
                }
                if (!(e instanceof Mob m) || (e instanceof DevilEntity d && d.spec().boss) || taken >= 5) {
                    continue;
                }
                boolean starving = e.getPersistentData().getLong(STARVED_UNTIL) > level.getGameTime()
                        || e.getHealth() < e.getMaxHealth() * 0.6f;
                if (!starving && taken >= 2) {
                    continue;
                }
                DevilEntity.enthrall(m, user.getUUID());
                m.getPersistentData().putLong(ControlMoves.THRALL_UNTIL, level.getGameTime() + 1200);
                m.setTarget(null);
                if (user instanceof Mob master && master.getTarget() != null) {
                    m.setTarget(master.getTarget());
                }
                Fx.stars(level, m.getEyePosition(), 6, 0.3);
                taken++;
            }
            if (user instanceof ServerPlayer sp) {
                sp.displayClientMessage(Component.translatable("msg.csm.dominated", taken), true);
            }
        }
    }

    /** She is simply somewhere else - usually right behind you. */
    public static class Vanish extends DevilAbility {
        public Vanish() {
            super(HybridType.FAMINE, "famine_vanish");
            timing(10, 80);
            cost(6);
            anim("famine_vanish", "vanish");
            ai(4, 20, 8);
            mobile();
            reach(24);
        }

        @Override
        public void perform(LivingEntity user, AbilityRun run) {
            if (run.tick != 4) {
                return;
            }
            ServerLevel level = level(user);
            LivingEntity t = target(run);
            Vec3 to;
            if (t != null) {
                Vec3 look = t.getLookAngle();
                Vec3 flat = new Vec3(look.x, 0, look.z);
                flat = flat.lengthSqr() > 1e-4 ? flat.normalize() : new Vec3(0, 0, 1);
                to = t.position().subtract(flat.scale(1.6 + t.getBbWidth()));
            } else {
                Vec3 hit = AbilityUtil.raycastBlock(user, 12).getLocation();
                to = hit.subtract(AbilityUtil.aim(user).scale(0.8));
            }
            if (!level.noCollision(user, user.getBoundingBox().move(to.subtract(user.position())))) {
                return;
            }
            Fx.smoke(level, user.getBoundingBox().getCenter(), 16, 0.5);
            AbilityUtil.sound(user, ModSounds.COSMOS_VOID.get(), 0.8f, 1.8f);
            user.teleportTo(to.x, to.y, to.z);
            if (t != null) {
                Vec3 d = t.position().subtract(to);
                float yaw = (float) (Math.atan2(-d.x, d.z) * 180 / Math.PI);
                user.setYRot(yaw);
                user.setYHeadRot(yaw);
            }
            user.fallDistance = 0;
            Fx.smoke(level, user.getBoundingBox().getCenter(), 16, 0.5);
        }
    }

    /** She eats. It heals her - and fills a stomach that is never full. */
    public static class Feast extends DevilAbility {
        public Feast() {
            super(HybridType.FAMINE, "famine_bite");
            anyForm();
            timing(18, 50);
            cost(0);
            anim("famine_bite", "bite");
            ai(0, 3, 12);
            reach(5);
        }

        @Override
        public void perform(LivingEntity user, AbilityRun run) {
            if (run.tick != 8) {
                return;
            }
            ServerLevel level = level(user);
            for (LivingEntity e : coneTargets(user, run, user.getEyePosition(), AbilityUtil.aim(user),
                    2.8 + user.getBbWidth() * 0.5, 55)) {
                AbilityUtil.sound(user, ModSounds.DEVIL_BITE.get(), 1.0f, 1.3f);
                AbilityUtil.hurtIgnoringIFrames(user, e, 10f);
                user.heal(6f);
                if (user instanceof Player p) {
                    p.getFoodData().eat(6, 0.8f);
                }
                AbilityUtil.blood(level, e.getBoundingBox().getCenter(), 30, 0.3);
                break;
            }
        }
    }

    private HumanDevilMoves() {
    }
}
