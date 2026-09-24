package com.csm.hybrids.ability.devil;

import com.csm.hybrids.ability.Ability;
import com.csm.hybrids.ability.AbilityRun;
import com.csm.hybrids.ability.AbilityUtil;
import com.csm.hybrids.fx.Fx;
import com.csm.hybrids.hybrid.HybridType;
import com.csm.hybrids.registry.ModParticles;
import com.csm.hybrids.registry.ModSounds;
import net.minecraft.core.BlockPos;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.phys.Vec3;

import java.util.ArrayList;
import java.util.List;

/** Calamities: the Gun Devil itself and the Typhoon Devil. */
public final class CalamityMoves {

    public static List<Ability> gunDevil() {
        return List.of(new Massacre(), new RifleVolley(), new BeltLash(), new BulletStorm());
    }

    public static List<Ability> typhoon() {
        return List.of(new Charge(), new Gale(), new Tornado(), new Hurl());
    }

    /** One bullet with a tracer; returns what it hit. */
    static LivingEntity fire(LivingEntity user, Vec3 muzzle, Vec3 dir, double range, float dmg) {
        ServerLevel level = (ServerLevel) user.level();
        AbilityUtil.Shot shot = AbilityUtil.shoot(user, muzzle, dir, range);
        Fx.bullet(level, muzzle, shot.end());
        if (shot.target() != null) {
            AbilityUtil.hurtIgnoringIFrames(user, shot.target(), dmg);
            AbilityUtil.blood(level, shot.end(), 8, 0.1);
        } else {
            level.sendParticles(ModParticles.SPARK.get(), shot.end().x, shot.end().y, shot.end().z, 3, 0.05, 0.05, 0.05,
                    0.15);
        }
        return shot.target();
    }

    static Vec3 rifleMuzzle(LivingEntity user, boolean right) {
        float h = user.getBbHeight();
        return user.position().add(0, h * 0.35, 0).add(AbilityUtil.right(user).scale((right ? 1 : -1) * user.getBbWidth()
                * 0.9)).add(AbilityUtil.aim(user).multiply(1, 0, 1).normalize().scale(user.getBbWidth() * 1.2));
    }

    // ================================================================== Gun Devil
    /** The massacre: in a heartbeat, a bullet for every living thing it can see. */
    public static class Massacre extends DevilAbility {
        public Massacre() {
            super(HybridType.GUN_DEVIL, "gundevil_massacre");
            timing(40, 600);
            cost(30);
            anim("", "massacre");
            fx("storm");
            ai(0, 48, 6);
            blind();
        }

        @Override
        public void perform(LivingEntity user, AbilityRun run) {
            ServerLevel level = level(user);
            Vec3 body = user.position().add(0, user.getBbHeight() * 0.7, 0);
            if (run.tick == 6) {
                AbilityUtil.sound(user, ModSounds.GUN_COCK.get(), 2.0f, 0.5f);
                for (LivingEntity e : AbilityUtil.inRadius(user, body, 48)) {
                    if (user.hasLineOfSight(e)) {
                        run.hit.add(e.getId());
                    }
                }
            }
            if (run.tick < 12 || run.tick > 32 || run.tick % 2 != 0) {
                return;
            }
            for (int id : run.hit) {
                if (level.getEntity(id) instanceof LivingEntity e && e.isAlive() && (run.tick + id) % 4 == 0) {
                    Vec3 m = body.add(level.random.nextGaussian() * user.getBbWidth() * 0.4, level.random.nextGaussian(),
                            level.random.nextGaussian() * user.getBbWidth() * 0.4);
                    fire(user, m, e.getBoundingBox().getCenter().subtract(m), 52, 5f);
                }
            }
            AbilityUtil.sound(user, ModSounds.GUN_SHOT.get(), 2.0f, 0.5f + level.random.nextFloat() * 0.4f);
        }
    }

    /** Both rifle arms swing up and pour fire at its target. */
    public static class RifleVolley extends DevilAbility {
        public RifleVolley() {
            super(HybridType.GUN_DEVIL, "gundevil_volley");
            timing(30, 60);
            cost(8);
            anim("", "volley");
            fx("volley");
            ai(3, 40, 12);
            reach(48);
        }

        @Override
        public void perform(LivingEntity user, AbilityRun run) {
            if (run.tick < 8 || run.tick > 24 || run.tick % 2 != 0) {
                return;
            }
            ServerLevel level = level(user);
            boolean right = (run.tick / 2) % 2 == 0;
            Vec3 m = rifleMuzzle(user, right);
            LivingEntity t = target(run);
            Vec3 aim = t != null ? t.getBoundingBox().getCenter().subtract(m) : AbilityUtil.aim(user);
            Vec3 dir = aim.normalize().add(level.random.nextGaussian() * 0.03, level.random.nextGaussian() * 0.03,
                    level.random.nextGaussian() * 0.03);
            fire(user, m, dir, 48, 6f);
            Fx.impact(level, m, 1.2);
            AbilityUtil.sound(user, ModSounds.GUN_CANNON.get(), 1.4f, 1.2f + level.random.nextFloat() * 0.2f);
        }
    }

    /** The ammunition belts it has for legs whip round it. */
    public static class BeltLash extends DevilAbility {
        public BeltLash() {
            super(HybridType.GUN_DEVIL, "gundevil_belts");
            timing(24, 80);
            cost(6);
            anim("", "belts");
            ai(0, 8, 10);
            blind();
        }

        @Override
        public void perform(LivingEntity user, AbilityRun run) {
            if (run.tick != 10) {
                return;
            }
            ServerLevel level = level(user);
            AbilityUtil.sound(user, ModSounds.WHIP_CRACK.get(), 1.6f, 0.5f);
            Vec3 c = user.position().add(0, user.getBbHeight() * 0.25, 0);
            for (LivingEntity e : AbilityUtil.inRadius(user, c, 9 + user.getBbWidth() * 0.5)) {
                AbilityUtil.hurtIgnoringIFrames(user, e, 12f);
                AbilityUtil.push(e, user.position(), 1.2, 0.4);
            }
            for (int k = 0; k < 6; k++) {
                double a = k * Math.PI / 3;
                Fx.whipArc(level, c, new Vec3(Math.cos(a), 0, Math.sin(a)), new Vec3(0, 1, 0), 9.0, 0.6);
            }
        }
    }

    /** Barrels erupt all over its body and fire in every direction. */
    public static class BulletStorm extends DevilAbility {
        public BulletStorm() {
            super(HybridType.GUN_DEVIL, "gundevil_storm");
            timing(40, 200);
            cost(15);
            anim("", "storm");
            fx("storm");
            ai(0, 20, 8);
            blind();
        }

        @Override
        public void perform(LivingEntity user, AbilityRun run) {
            if (run.tick < 6 || run.tick > 34 || run.tick % 2 != 0) {
                return;
            }
            ServerLevel level = level(user);
            Vec3 body = user.position().add(0, user.getBbHeight() * 0.6, 0);
            for (int k = 0; k < 6; k++) {
                double a = level.random.nextDouble() * Math.PI * 2;
                Vec3 dir = new Vec3(Math.cos(a), level.random.nextGaussian() * 0.25 - 0.1, Math.sin(a));
                fire(user, body.add(dir.scale(user.getBbWidth() * 0.5)), dir, 28, 4f);
            }
            for (LivingEntity e : AbilityUtil.inRadius(user, body, 20)) {
                if (level.random.nextFloat() < 0.35f) {
                    fire(user, body, e.getBoundingBox().getCenter().subtract(body), 24, 4f);
                }
            }
            AbilityUtil.sound(user, ModSounds.GUN_SHOT.get(), 1.8f, 0.7f + level.random.nextFloat() * 0.5f);
        }
    }

    // ================================================================== Typhoon Devil
    /** It charges straight through everything - buildings included - and hurls whatever it hits. */
    public static class Charge extends DevilAbility {
        public Charge() {
            super(HybridType.TYPHOON, "typhoon_charge");
            timing(30, 120);
            cost(10);
            anim("", "charge");
            ai(4, 20, 10);
            mobile();
            reach(24);
        }

        @Override
        public void perform(LivingEntity user, AbilityRun run) {
            ServerLevel level = level(user);
            if (run.tick == 0) {
                LivingEntity t = target(run);
                Vec3 d = t != null ? t.position().subtract(user.position()) : AbilityUtil.aim(user);
                run.vec = new Vec3(d.x, 0, d.z).normalize();
                AbilityUtil.sound(user, ModSounds.DEVIL_ROAR.get(), 2.0f, 0.6f);
            }
            if (run.tick < 6 || run.tick > 26 || run.vec == null) {
                return;
            }
            user.setDeltaMovement(run.vec.x * 1.1, user.getDeltaMovement().y, run.vec.z * 1.1);
            user.hurtMarked = true;
            Vec3 front = user.position().add(run.vec.scale(user.getBbWidth() * 0.6));
            if (run.tick % 2 == 0) {
                Fx.clods(level, user.position(), 6, 0.35);
                Fx.shockwave(level, user.position(), 2.5, Fx.STEEL_RING);
                AbilityUtil.sound(user, ModSounds.DEVIL_SLAM.get(), 0.9f, 1.2f);
            }
            for (LivingEntity e : AbilityUtil.inRadius(user, front.add(0, user.getBbHeight() * 0.4, 0),
                    user.getBbWidth() * 0.7 + 1.5)) {
                if (run.hit.add(e.getId())) {
                    AbilityUtil.hurtIgnoringIFrames(user, e, 18f);
                    e.setDeltaMovement(run.vec.x * 2.2, 0.9, run.vec.z * 2.2);
                    e.hurtMarked = true;
                    Fx.impact(level, e.getBoundingBox().getCenter(), 2.0);
                }
            }
            if (AbilityUtil.griefing(level)) {
                smash(level, user, front);
            }
        }

        static void smash(ServerLevel level, LivingEntity user, Vec3 front) {
            int r = (int) Math.ceil(user.getBbWidth() * 0.5);
            int h = (int) Math.ceil(user.getBbHeight());
            BlockPos base = BlockPos.containing(front);
            for (int dx = -r; dx <= r; dx++) {
                for (int dz = -r; dz <= r; dz++) {
                    for (int dy = 1; dy <= h; dy++) {
                        BlockPos p = base.offset(dx, dy, dz);
                        BlockState st = level.getBlockState(p);
                        if (!st.isAir() && st.getDestroySpeed(level, p) >= 0 && st.getDestroySpeed(level, p) < 3.5f) {
                            level.destroyBlock(p, level.random.nextFloat() < 0.2f, user);
                        }
                    }
                }
            }
        }
    }

    /** A blast of wind that flings everything in front of it away. */
    public static class Gale extends DevilAbility {
        public Gale() {
            super(HybridType.TYPHOON, "typhoon_gale");
            timing(24, 80);
            cost(8);
            anim("", "gale");
            ai(2, 16, 12);
        }

        @Override
        public void perform(LivingEntity user, AbilityRun run) {
            if (run.tick != 11) {
                return;
            }
            ServerLevel level = level(user);
            Vec3 aim = AbilityUtil.aim(user);
            Vec3 from = user.position().add(0, user.getBbHeight() * 0.5, 0);
            AbilityUtil.sound(user, ModSounds.DEVIL_GUST.get(), 2.0f, 0.8f);
            for (LivingEntity e : coneTargets(user, run, from, aim, 18, 45)) {
                AbilityUtil.hurtIgnoringIFrames(user, e, 10f);
                e.setDeltaMovement(aim.x * 2.6, 1.0, aim.z * 2.6);
                e.hurtMarked = true;
            }
            for (int k = 0; k < 24; k++) {
                Vec3 off = new Vec3(level.random.nextGaussian(), level.random.nextGaussian() * 0.6,
                        level.random.nextGaussian()).scale(2.0);
                Vec3 p = from.add(aim.scale(2 + level.random.nextDouble() * 10)).add(off);
                Fx.speedLine(level, p, p.add(aim.scale(4)));
            }
        }
    }

    /** It becomes the eye of a storm: everything around it is sucked in, lifted and battered, then flung away. */
    public static class Tornado extends DevilAbility {
        public Tornado() {
            super(HybridType.TYPHOON, "typhoon_tornado");
            timing(80, 300);
            cost(20);
            anim("", "tornado");
            ai(0, 12, 8);
            blind();
        }

        @Override
        public void perform(LivingEntity user, AbilityRun run) {
            ServerLevel level = level(user);
            Vec3 c = user.position();
            if (run.tick % 10 == 0) {
                AbilityUtil.sound(user, ModSounds.DEVIL_GUST.get(), 1.8f, 0.6f + run.tick * 0.005f);
            }
            if (run.tick < 10 || run.tick > 70) {
                return;
            }
            for (int k = 0; k < 4; k++) {
                double a = (run.tick * 0.5 + k * Math.PI / 2);
                double r = 3 + (run.tick % 20) * 0.4;
                Vec3 p = c.add(Math.cos(a) * r, 1 + k * 2.0, Math.sin(a) * r);
                Vec3 tan = new Vec3(-Math.sin(a), 0.3, Math.cos(a));
                Fx.speedLine(level, p, p.add(tan.scale(3.0)));
            }
            boolean last = run.tick == 70;
            for (LivingEntity e : AbilityUtil.inRadius(user, c.add(0, 2, 0), 14)) {
                Vec3 to = c.subtract(e.position());
                Vec3 flat = new Vec3(to.x, 0, to.z);
                Vec3 swirl = new Vec3(-flat.z, 0, flat.x).normalize();
                if (last) {
                    AbilityUtil.push(e, c, 2.2, 0.8);
                    AbilityUtil.hurtIgnoringIFrames(user, e, 8f);
                    continue;
                }
                Vec3 pull = flat.lengthSqr() > 4 ? flat.normalize().scale(0.18) : Vec3.ZERO;
                e.setDeltaMovement(pull.add(swirl.scale(0.35)).add(0, e.getY() < c.y + 6 ? 0.12 : 0.02, 0));
                e.fallDistance = 0;
                e.hurtMarked = true;
                if (run.tick % 5 == 0) {
                    AbilityUtil.hurtIgnoringIFrames(user, e, 2f);
                }
            }
        }
    }

    /** It tears up rubble and hurls it. */
    public static class Hurl extends DevilAbility {
        public Hurl() {
            super(HybridType.TYPHOON, "typhoon_hurl");
            timing(26, 90);
            cost(10);
            anim("", "hurl");
            ai(5, 30, 10);
            reach(40);
        }

        @Override
        public void perform(LivingEntity user, AbilityRun run) {
            ServerLevel level = level(user);
            if (run.tick == 6) {
                Fx.clods(level, user.position(), 20, 0.4);
                AbilityUtil.sound(user, ModSounds.DEVIL_SLAM.get(), 1.2f, 0.8f);
            }
            if (run.tick != 15) {
                return;
            }
            Vec3 from = user.position().add(0, user.getBbHeight() * 0.95, 0);
            LivingEntity t = target(run);
            Vec3 to = t != null ? t.getBoundingBox().getCenter() : from.add(AbilityUtil.aim(user).scale(30));
            List<Vec3> path = new ArrayList<>();
            for (int k = 0; k <= 12; k++) {
                double s = k / 12.0;
                path.add(from.lerp(to, s).add(0, Math.sin(s * Math.PI) * 4.0, 0));
            }
            for (Vec3 p : path) {
                level.sendParticles(ModParticles.CLOD.get(), p.x, p.y, p.z, 3, 0.3, 0.3, 0.3, 0.05);
            }
            AbilityUtil.sound(user, ModSounds.DEVIL_GUST.get(), 1.4f, 1.3f);
            Fx.impact(level, to, 2.4);
            Fx.shockwave(level, to.subtract(0, 1, 0), 3.5, Fx.STEEL_RING);
            Fx.clods(level, to, 24, 0.5);
            for (LivingEntity e : AbilityUtil.inRadius(user, to, 3.5)) {
                AbilityUtil.hurtIgnoringIFrames(user, e, 16f);
                AbilityUtil.push(e, to, 1.0, 0.5);
            }
        }
    }

    private CalamityMoves() {
    }
}
