package com.csm.hybrids.ability.devil;

import com.csm.hybrids.ability.Ability;
import com.csm.hybrids.ability.AbilityRun;
import com.csm.hybrids.ability.AbilityUtil;
import com.csm.hybrids.entity.devil.DevilEntity;
import com.csm.hybrids.fx.Fx;
import com.csm.hybrids.hybrid.HybridLogic;
import com.csm.hybrids.hybrid.HybridType;
import com.csm.hybrids.registry.ModParticles;
import com.csm.hybrids.registry.ModSounds;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.effect.MobEffectInstance;
import net.minecraft.world.effect.MobEffects;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.Mob;
import net.minecraft.world.entity.MobSpawnType;
import net.minecraft.world.entity.monster.Zombie;
import net.minecraft.world.phys.AABB;
import net.minecraft.world.phys.Vec3;

import java.util.List;

/** The weaker devils of the early Public Safety days: the Zombie, Tomato and Sea Cucumber Devils. */
public final class EarlyDevilMoves {
    public static final String BITTEN_BY = "csm_bitten_by";
    public static final String BITTEN_UNTIL = "csm_bitten_until";

    public static List<Ability> zombie() {
        return List.of(new ZombieBite(), new Horde(), new Tendrils(), new Feast());
    }

    public static List<Ability> tomato() {
        return List.of(new ArmSlam(), new SeedSpray(), new JuiceBurst(), new ManyHands());
    }

    public static List<Ability> seaCucumber() {
        return List.of(new FingerGrab(), new Spew(), new BodySlam(), new Regenerate());
    }

    static void heal(LivingEntity user, float amount) {
        user.heal(amount);
        if (user instanceof ServerPlayer sp) {
            HybridLogic.addBlood(sp, amount);
        }
    }

    /** A zombie that serves {@code master} for two minutes (a husk: the dead it raises don't burn in daylight). */
    public static Zombie raiseZombie(ServerLevel level, Vec3 at, LivingEntity master) {
        Zombie z = EntityType.HUSK.create(level);
        if (z == null) {
            return null;
        }
        z.moveTo(at.x, at.y, at.z, level.random.nextFloat() * 360f, 0);
        z.finalizeSpawn(level, level.getCurrentDifficultyAt(z.blockPosition()), MobSpawnType.MOB_SUMMONED, null, null);
        z.setBaby(false);
        DevilEntity.enthrall(z, master.getUUID());
        z.getPersistentData().putLong(ControlMoves.THRALL_UNTIL, level.getGameTime() + 2400);
        if (master instanceof Mob mob && mob.getTarget() != null) {
            z.setTarget(mob.getTarget());
        }
        level.addFreshEntity(z);
        Fx.clods(level, at, 8, 0.3);
        AbilityUtil.blood(level, at.add(0, 1, 0), 16, 0.4);
        return z;
    }

    // ================================================================== Zombie Devil
    /** A bite that turns: anything it kills in the next ten seconds rises as one of its zombies. */
    public static class ZombieBite extends DevilAbility {
        public ZombieBite() {
            super(HybridType.ZOMBIE, "zombie_bite");
            timing(20, 50);
            cost(4);
            anim("", "bite");
            ai(0, 4, 12);
        }

        @Override
        public void perform(LivingEntity user, AbilityRun run) {
            if (run.tick != 9) {
                return;
            }
            ServerLevel level = level(user);
            AbilityUtil.sound(user, ModSounds.DEVIL_BITE.get(), 1.3f, 0.7f);
            for (LivingEntity e : coneTargets(user, run, user.getEyePosition(), AbilityUtil.aim(user),
                    4.0 + user.getBbWidth() * 0.5, 60)) {
                e.getPersistentData().putUUID(BITTEN_BY, user.getUUID());
                e.getPersistentData().putLong(BITTEN_UNTIL, level.getGameTime() + 200);
                AbilityUtil.hurtIgnoringIFrames(user, e, 11f);
                e.addEffect(AbilityUtil.quiet(new MobEffectInstance(MobEffects.HUNGER, 200, 1)));
                e.addEffect(AbilityUtil.quiet(new MobEffectInstance(MobEffects.WEAKNESS, 200, 0)));
                AbilityUtil.blood(level, e.getBoundingBox().getCenter(), 30, 0.3);
                heal(user, 3f);
            }
        }
    }

    /** Its tendrils plunge into the ground and the dead crawl up round its prey. */
    public static class Horde extends DevilAbility {
        public Horde() {
            super(HybridType.ZOMBIE, "zombie_horde");
            timing(40, 400);
            cost(20);
            anim("", "horde");
            ai(0, 30, 8);
            blind();
        }

        @Override
        public void perform(LivingEntity user, AbilityRun run) {
            ServerLevel level = level(user);
            if (run.tick == 10) {
                AbilityUtil.sound(user, ModSounds.DEVIL_GROWL.get(), 1.6f, 0.6f);
            }
            if (run.tick < 16 || run.tick > 28 || run.tick % 4 != 0) {
                return;
            }
            LivingEntity t = target(run);
            Vec3 around = t != null ? t.position() : user.position().add(AbilityUtil.aim(user).scale(6));
            double a = level.random.nextDouble() * Math.PI * 2;
            Vec3 at = around.add(Math.cos(a) * 3.0, 0, Math.sin(a) * 3.0);
            Vec3 ground = AbilityUtil.groundBelow(level, at.add(0, 2, 0), 8);
            raiseZombie(level, ground != null ? ground : at, user);
            AbilityUtil.sound(user, ModSounds.DEVIL_SLAM.get(), 0.6f, 1.4f);
        }
    }

    /** The brain's tendrils whip all round it. */
    public static class Tendrils extends DevilAbility {
        public Tendrils() {
            super(HybridType.ZOMBIE, "zombie_tendrils");
            timing(24, 80);
            cost(8);
            anim("", "tendrils");
            ai(0, 7, 10);
            blind();
        }

        @Override
        public void perform(LivingEntity user, AbilityRun run) {
            if (run.tick != 11) {
                return;
            }
            ServerLevel level = level(user);
            AbilityUtil.sound(user, ModSounds.WHIP_CRACK.get(), 1.2f, 0.6f);
            Vec3 c = user.position().add(0, user.getBbHeight() * 0.6, 0);
            for (LivingEntity e : AbilityUtil.inRadius(user, c, 7.5 + user.getBbWidth() * 0.5)) {
                AbilityUtil.hurtIgnoringIFrames(user, e, 8f);
                AbilityUtil.push(e, user.position(), -0.6, 0.35);
                AbilityUtil.blood(level, e.getBoundingBox().getCenter(), 10, 0.2);
            }
            for (int k = 0; k < 6; k++) {
                double a = k * Math.PI / 3;
                Vec3 d = new Vec3(Math.cos(a), -0.2, Math.sin(a));
                Fx.whipArc(level, c.add(0, user.getBbHeight() * 0.3, 0), d, new Vec3(0, 1, 0), 7.0, 0.5);
            }
        }
    }

    /** It gorges on its own zombies (or on blood if it has none) to heal. */
    public static class Feast extends DevilAbility {
        public Feast() {
            super(HybridType.ZOMBIE, "zombie_feast");
            timing(40, 300);
            cost(0);
            anim("", "feast");
            ai(0, 40, 12);
            blind();
        }

        @Override
        public boolean aiReady(DevilEntity mob, LivingEntity target) {
            return mob.getHealth() < mob.getMaxHealth() * 0.5f;
        }

        @Override
        public void perform(LivingEntity user, AbilityRun run) {
            if (run.tick != 20) {
                return;
            }
            ServerLevel level = level(user);
            int eaten = 0;
            for (Mob m : level.getEntitiesOfClass(Mob.class, new AABB(user.position(), user.position()).inflate(16),
                    m -> m.getPersistentData().hasUUID(DevilEntity.THRALL_TAG)
                            && m.getPersistentData().getUUID(DevilEntity.THRALL_TAG).equals(user.getUUID()))) {
                if (eaten++ >= 5) {
                    break;
                }
                Vec3 c = m.getBoundingBox().getCenter();
                AbilityUtil.blood(level, c, 40, 0.4);
                Fx.bloodSpray(level, c, user.getBoundingBox().getCenter().subtract(c).normalize(), 20, 0.6);
                m.kill();
                heal(user, user.getMaxHealth() * 0.08f);
            }
            if (eaten == 0) {
                heal(user, user.getMaxHealth() * 0.1f);
            }
            AbilityUtil.sound(user, ModSounds.BLOOD_DRINK.get(), 1.4f, 0.5f);
        }
    }

    // ================================================================== Tomato Devil
    /** Its front arms rear up and slam down on whatever is in front of it. */
    public static class ArmSlam extends DevilAbility {
        public ArmSlam() {
            super(HybridType.TOMATO, "tomato_slam");
            timing(18, 45);
            cost(4);
            anim("", "slam");
            ai(0, 4, 14);
        }

        @Override
        public void perform(LivingEntity user, AbilityRun run) {
            if (run.tick != 10) {
                return;
            }
            ServerLevel level = level(user);
            Vec3 aim = AbilityUtil.aim(user);
            Vec3 at = user.position().add(aim.multiply(1, 0, 1).normalize().scale(user.getBbWidth() * 0.5 + 1.6));
            AbilityUtil.sound(user, ModSounds.DEVIL_SLAM.get(), 1.0f, 1.3f);
            Fx.shockwave(level, at, 2.8, Fx.STEEL_RING);
            Fx.clods(level, at, 10, 0.35);
            for (LivingEntity e : AbilityUtil.inRadius(user, at.add(0, 0.8, 0), 3.0)) {
                AbilityUtil.hurtIgnoringIFrames(user, e, 10f);
                AbilityUtil.push(e, at, 0.8, 0.45);
            }
        }
    }

    /** It squeezes and spits a spray of hard seeds. */
    public static class SeedSpray extends DevilAbility {
        public SeedSpray() {
            super(HybridType.TOMATO, "tomato_seeds");
            timing(20, 60);
            cost(5);
            anim("", "seeds");
            ai(3, 14, 10);
        }

        @Override
        public void perform(LivingEntity user, AbilityRun run) {
            if (run.tick < 9 || run.tick > 13) {
                return;
            }
            ServerLevel level = level(user);
            Vec3 mouth = user.position().add(0, user.getBbHeight() * 0.55, 0).add(AbilityUtil.aim(user).scale(
                    user.getBbWidth() * 0.55));
            LivingEntity t = target(run);
            Vec3 base = t != null ? t.getBoundingBox().getCenter().subtract(mouth).normalize() : AbilityUtil.aim(user);
            for (int k = 0; k < 3; k++) {
                Vec3 dir = base.add(level.random.nextGaussian() * 0.08, level.random.nextGaussian() * 0.06,
                        level.random.nextGaussian() * 0.08).normalize();
                AbilityUtil.Shot shot = AbilityUtil.shoot(user, mouth, dir, 16);
                Fx.speedLine(level, mouth, shot.end());
                if (shot.target() != null) {
                    AbilityUtil.hurtIgnoringIFrames(user, shot.target(), 1.5f);
                }
                level.sendParticles(ModParticles.CLOD.get(), shot.end().x, shot.end().y, shot.end().z, 2, 0.05, 0.05,
                        0.05, 0.08);
            }
            AbilityUtil.sound(user, ModSounds.GUN_SHOT.get(), 0.5f, 1.8f);
        }
    }

    /** It swells and bursts a spray of stinging juice all round itself. */
    public static class JuiceBurst extends DevilAbility {
        public JuiceBurst() {
            super(HybridType.TOMATO, "tomato_burst");
            timing(22, 120);
            cost(6);
            anim("", "burst");
            ai(0, 5, 8);
            blind();
        }

        @Override
        public void perform(LivingEntity user, AbilityRun run) {
            if (run.tick != 11) {
                return;
            }
            ServerLevel level = level(user);
            Vec3 c = user.position().add(0, user.getBbHeight() * 0.5, 0);
            AbilityUtil.sound(user, ModSounds.BLOOD_SLAM.get(), 1.2f, 1.2f);
            AbilityUtil.blood(level, c, 90, 1.2);
            Fx.shockwave(level, user.position(), 5.5, Fx.BLOOD_RING);
            for (LivingEntity e : AbilityUtil.inRadius(user, c, 5.5)) {
                AbilityUtil.hurtIgnoringIFrames(user, e, 5f);
                e.addEffect(AbilityUtil.quiet(new MobEffectInstance(MobEffects.BLINDNESS, 60, 0)));
                AbilityUtil.push(e, user.position(), 0.6, 0.2);
            }
        }
    }

    /** Two of its hands grab hold and pummel. */
    public static class ManyHands extends DevilAbility {
        public ManyHands() {
            super(HybridType.TOMATO, "tomato_grab");
            timing(24, 70);
            cost(5);
            anim("", "grab");
            ai(0, 3, 10);
        }

        @Override
        public void perform(LivingEntity user, AbilityRun run) {
            if (run.tick != 6 && run.tick != 10 && run.tick != 14 && run.tick != 18) {
                return;
            }
            ServerLevel level = level(user);
            for (LivingEntity e : coneTargets(user, run, user.getEyePosition(), AbilityUtil.aim(user),
                    3.2 + user.getBbWidth() * 0.5, 70)) {
                AbilityUtil.hurtIgnoringIFrames(user, e, 4f);
                e.setDeltaMovement(e.getDeltaMovement().scale(0.2));
                e.hurtMarked = true;
                Fx.impact(level, e.getBoundingBox().getCenter(), 0.8);
                AbilityUtil.sound(user, ModSounds.VIOLENCE_PUNCH.get(), 0.7f, 1.3f);
                break;
            }
        }
    }

    // ================================================================== Sea Cucumber Devil
    /** Fingers all over its body seize whatever is close. */
    public static class FingerGrab extends DevilAbility {
        public FingerGrab() {
            super(HybridType.SEA_CUCUMBER, "seacu_grab");
            timing(20, 50);
            cost(3);
            anim("", "grab");
            ai(0, 3, 14);
        }

        @Override
        public void perform(LivingEntity user, AbilityRun run) {
            if (run.tick != 9) {
                return;
            }
            ServerLevel level = level(user);
            for (LivingEntity e : coneTargets(user, run, user.getEyePosition(), AbilityUtil.aim(user),
                    3.0 + user.getBbWidth() * 0.5, 70)) {
                AbilityUtil.hurtIgnoringIFrames(user, e, 6f);
                e.addEffect(AbilityUtil.quiet(new MobEffectInstance(MobEffects.MOVEMENT_SLOWDOWN, 60, 3)));
                AbilityUtil.blood(level, e.getBoundingBox().getCenter(), 12, 0.2);
                AbilityUtil.sound(user, ModSounds.DEVIL_BITE.get(), 0.8f, 1.5f);
                break;
            }
        }
    }

    /** Like a real sea cucumber it throws out its own guts: sticky and poisonous. */
    public static class Spew extends DevilAbility {
        public Spew() {
            super(HybridType.SEA_CUCUMBER, "seacu_spew");
            timing(28, 90);
            cost(6);
            anim("", "spew");
            fx("spew");
            ai(1, 8, 10);
        }

        @Override
        public void perform(LivingEntity user, AbilityRun run) {
            if (run.tick != 12) {
                return;
            }
            ServerLevel level = level(user);
            Vec3 top = user.position().add(0, user.getBbHeight(), 0);
            Vec3 aim = AbilityUtil.aim(user);
            AbilityUtil.sound(user, ModSounds.BLOOD_FORM.get(), 1.2f, 0.8f);
            for (int k = 0; k < 6; k++) {
                Vec3 p = top.add(aim.scale(1.5 + k * 1.2)).add(0, -k * 0.35, 0);
                Fx.gore(level, p, 2);
                AbilityUtil.blood(level, p, 8, 0.3);
            }
            for (LivingEntity e : coneTargets(user, run, top, aim, 8, 35)) {
                AbilityUtil.hurtIgnoringIFrames(user, e, 4f);
                e.addEffect(AbilityUtil.quiet(new MobEffectInstance(MobEffects.POISON, 80, 1)));
                e.addEffect(AbilityUtil.quiet(new MobEffectInstance(MobEffects.MOVEMENT_SLOWDOWN, 80, 2)));
            }
        }
    }

    /** It topples onto its prey with all its weight. */
    public static class BodySlam extends DevilAbility {
        public BodySlam() {
            super(HybridType.SEA_CUCUMBER, "seacu_slam");
            timing(20, 70);
            cost(4);
            anim("", "slam");
            ai(0, 3, 8);
        }

        @Override
        public void perform(LivingEntity user, AbilityRun run) {
            if (run.tick != 11) {
                return;
            }
            ServerLevel level = level(user);
            Vec3 at = user.position().add(AbilityUtil.aim(user).multiply(1, 0, 1).normalize().scale(user.getBbHeight() * 0.7));
            AbilityUtil.sound(user, ModSounds.DEVIL_SLAM.get(), 0.9f, 1.4f);
            Fx.shockwave(level, at, 2.2, Fx.BLOOD_RING);
            for (LivingEntity e : AbilityUtil.inRadius(user, at.add(0, 0.6, 0), 2.4)) {
                AbilityUtil.hurtIgnoringIFrames(user, e, 8f);
                e.addEffect(AbilityUtil.quiet(new MobEffectInstance(MobEffects.MOVEMENT_SLOWDOWN, 40, 1)));
            }
        }
    }

    /** It knits itself back together. */
    public static class Regenerate extends DevilAbility {
        public Regenerate() {
            super(HybridType.SEA_CUCUMBER, "seacu_regen");
            timing(40, 300);
            cost(10);
            anim("", "regen");
            ai(0, 40, 14);
            blind();
        }

        @Override
        public boolean aiReady(DevilEntity mob, LivingEntity target) {
            return mob.getHealth() < mob.getMaxHealth() * 0.6f;
        }

        @Override
        public void perform(LivingEntity user, AbilityRun run) {
            if (run.tick % 5 == 0) {
                user.heal(user.getMaxHealth() * 0.04f);
                AbilityUtil.blood(level(user), user.getBoundingBox().getCenter(), 4, 0.4);
            }
        }
    }

    private EarlyDevilMoves() {
    }
}
