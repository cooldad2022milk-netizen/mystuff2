package com.csm.hybrids.fx;

import com.csm.hybrids.registry.ModParticles;
import net.minecraft.core.particles.SimpleParticleType;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.phys.Vec3;

/**
 * Server-side effect helpers. Everything is sent as the mod's own particles.
 * <p>
 * "Parameter" particles (slash, shockwave, speed line, impact) are sent with count 0 so the client receives the
 * exact vector, which those particles read as orientation/size instead of motion.
 */
public final class Fx {
    public static final int FIRE_RING = 0;
    public static final int BLOOD_RING = 1;
    public static final int STEEL_RING = 2;

    private static void exact(ServerLevel level, SimpleParticleType type, Vec3 p, double vx, double vy, double vz) {
        level.sendParticles(type, p.x, p.y, p.z, 0, vx, vy, vz, 1.0);
    }

    // ------------------------------------------------------------------ gore
    public static void blood(ServerLevel level, Vec3 p, int count, double spread) {
        level.sendParticles(ModParticles.BLOOD.get(), p.x, p.y, p.z, count, spread, spread * 0.8, spread, 0.25);
        level.sendParticles(ModParticles.BLOOD_MIST.get(), p.x, p.y, p.z, Math.max(1, count / 5), spread * 0.6,
                spread * 0.5, spread * 0.6, 0.03);
    }

    public static void gore(ServerLevel level, Vec3 p, int count) {
        level.sendParticles(ModParticles.GORE.get(), p.x, p.y, p.z, count, 0.2, 0.2, 0.2, 0.3);
    }

    /** A spray of blood thrown in one direction (chainsaw exit wounds, cuts). */
    public static void bloodSpray(ServerLevel level, Vec3 p, Vec3 dir, int count, double speed) {
        for (int i = 0; i < count; i++) {
            Vec3 d = dir.add(level.random.nextGaussian() * 0.35, level.random.nextGaussian() * 0.35 + 0.15,
                    level.random.nextGaussian() * 0.35).normalize().scale(speed * (0.5 + level.random.nextDouble()));
            exact(level, ModParticles.BLOOD.get(), p, d.x, d.y, d.z);
        }
    }

    // ------------------------------------------------------------------ metal
    public static void sparks(ServerLevel level, Vec3 p, Vec3 dir, int count, double speed) {
        for (int i = 0; i < count; i++) {
            Vec3 d = dir.add(level.random.nextGaussian() * 0.5, level.random.nextGaussian() * 0.5 + 0.2,
                    level.random.nextGaussian() * 0.5).normalize().scale(speed * (0.4 + level.random.nextDouble()));
            exact(level, ModParticles.SPARK.get(), p, d.x, d.y, d.z);
        }
    }

    public static void shards(ServerLevel level, Vec3 p, int count, double speed) {
        level.sendParticles(ModParticles.SHARD.get(), p.x, p.y, p.z, count, 0.25, 0.3, 0.25, speed);
    }

    /** Chainsaw cut crescent in front of {@code p}, facing {@code dir}; {@code size} in blocks. */
    public static void slash(ServerLevel level, Vec3 p, Vec3 dir, double size) {
        Vec3 d = dir.normalize().scale(size);
        exact(level, ModParticles.SLASH.get(), p, d.x, d.y, d.z);
    }

    // ------------------------------------------------------------------ fire
    public static void fireJet(ServerLevel level, Vec3 from, Vec3 dir, int count, double speed, double spread) {
        for (int i = 0; i < count; i++) {
            Vec3 d = dir.add(level.random.nextGaussian() * spread, level.random.nextGaussian() * spread,
                    level.random.nextGaussian() * spread).normalize().scale(speed * (0.7 + level.random.nextDouble() * 0.6));
            exact(level, i % 6 == 0 ? ModParticles.EMBER.get() : ModParticles.FIRE.get(), from, d.x, d.y, d.z);
        }
    }

    public static void fireBurst(ServerLevel level, Vec3 p, int count, double speed) {
        for (int i = 0; i < count; i++) {
            double a = i / (double) count * Math.PI * 2;
            exact(level, ModParticles.FIRE.get(), p, Math.cos(a) * speed, 0.02 + level.random.nextDouble() * 0.05,
                    Math.sin(a) * speed);
        }
        level.sendParticles(ModParticles.EMBER.get(), p.x, p.y + 0.5, p.z, count / 3, 0.6, 0.4, 0.6, 0.08);
    }

    public static void smoke(ServerLevel level, Vec3 p, int count, double spread) {
        level.sendParticles(ModParticles.SMOKE.get(), p.x, p.y, p.z, count, spread, spread * 0.6, spread, 0.02);
    }

    public static void embers(ServerLevel level, Vec3 p, int count, double spread) {
        level.sendParticles(ModParticles.EMBER.get(), p.x, p.y, p.z, count, spread, spread, spread, 0.05);
    }

    // ------------------------------------------------------------------ impact
    public static void shockwave(ServerLevel level, Vec3 p, double radius, int variant) {
        exact(level, ModParticles.SHOCKWAVE.get(), p.add(0, 0.08, 0), radius, variant, 0);
    }

    public static void impact(ServerLevel level, Vec3 p, double size) {
        exact(level, ModParticles.IMPACT.get(), p, size * 0.75, 0, 0);
    }

    public static void speedLine(ServerLevel level, Vec3 from, Vec3 to) {
        Vec3 d = to.subtract(from);
        exact(level, ModParticles.SPEED_LINE.get(), from, d.x, d.y, d.z);
    }

    public static void charge(ServerLevel level, Vec3 center, int count, double radius) {
        for (int i = 0; i < count; i++) {
            Vec3 off = new Vec3(level.random.nextGaussian(), level.random.nextGaussian(), level.random.nextGaussian())
                    .normalize().scale(radius);
            Vec3 v = off.scale(-0.12);
            Vec3 p = center.add(off);
            exact(level, ModParticles.CHARGE.get(), p, v.x, v.y, v.z);
        }
    }

    public static void exhaust(ServerLevel level, Vec3 p, int count) {
        level.sendParticles(ModParticles.EXHAUST.get(), p.x, p.y, p.z, count, 0.15, 0.1, 0.15, 0.02);
    }

    // ------------------------------------------------------------------ bomb
    /** Fireball bloom + ring of fire + smoke column + embers + shockwave. */
    public static void explosion(ServerLevel level, Vec3 p, double radius) {
        exact(level, ModParticles.BLAST.get(), p, radius * 0.9, 0, 0);
        for (int i = 0; i < 3; i++) {
            Vec3 o = p.add(level.random.nextGaussian() * radius * 0.25, level.random.nextGaussian() * radius * 0.2,
                    level.random.nextGaussian() * radius * 0.25);
            exact(level, ModParticles.BLAST.get(), o, radius * (0.4 + level.random.nextDouble() * 0.3), 0, 0);
        }
        fireBurst(level, p, (int) (16 + radius * 8), 0.12 + radius * 0.06);
        fireJet(level, p, new Vec3(0, 1, 0), (int) (8 + radius * 4), 0.18 + radius * 0.05, 0.6);
        smoke(level, p.add(0, radius * 0.4, 0), (int) (1 + radius * 1.5), radius * 0.3);
        embers(level, p, (int) (10 + radius * 6), radius * 0.4);
        shockwave(level, new Vec3(p.x, Math.floor(p.y) + 0.02, p.z), radius * 1.4, FIRE_RING);
        impact(level, p, radius * 0.7);
    }

    /** A lit-fuse sparkle (bomb fuses, the explosive spark projectile). */
    public static void fuseSparks(ServerLevel level, Vec3 p, int count) {
        sparks(level, p, new Vec3(0, 1, 0), count, 0.15);
        level.sendParticles(ModParticles.EMBER.get(), p.x, p.y, p.z, Math.max(1, count / 2), 0.05, 0.05, 0.05, 0.02);
    }

    // ------------------------------------------------------------------ whip
    /** A whip cracking along a curved path: chained streaks with a snap-flash at the tip. */
    public static void whipArc(ServerLevel level, Vec3 from, Vec3 dir, Vec3 bendAxis, double length, double curl) {
        Vec3 d = dir.normalize();
        Vec3 side = bendAxis.normalize();
        int segs = 7;
        Vec3 prev = from;
        for (int i = 1; i <= segs; i++) {
            double t = i / (double) segs;
            Vec3 p = from.add(d.scale(length * t)).add(side.scale(Math.sin(t * Math.PI) * curl));
            Vec3 seg = p.subtract(prev);
            exact(level, ModParticles.WHIP_TRAIL.get(), prev, seg.x, seg.y, seg.z);
            prev = p;
        }
        impact(level, prev, 0.6);
        sparks(level, prev, d, 4, 0.25);
    }

    // ------------------------------------------------------------------ fiends / new hybrids
    /** A bullet: tracer from the muzzle to where it hit, plus a muzzle flash. */
    public static void bullet(ServerLevel level, Vec3 muzzle, Vec3 hit) {
        Vec3 d = hit.subtract(muzzle);
        exact(level, ModParticles.BULLET.get(), muzzle, d.x, d.y, d.z);
        impact(level, muzzle, 0.35);
        level.sendParticles(ModParticles.SPARK.get(), muzzle.x, muzzle.y, muzzle.z, 3, 0.03, 0.03, 0.03, 0.12);
    }

    /** A chain from {@code from} to {@code to} that hangs there for {@code life} ticks. */
    public static void chain(ServerLevel level, Vec3 from, Vec3 to, int life) {
        Vec3 d = to.subtract(from);
        // identical chains with random lifetimes overlap exactly; the longer the wanted life, the more of them
        for (int k = 0; k < Math.max(1, life / 10); k++) {
            exact(level, ModParticles.CHAIN.get(), from, d.x, d.y, d.z);
        }
    }

    public static void stars(ServerLevel level, Vec3 p, int count, double spread) {
        level.sendParticles(ModParticles.STAR.get(), p.x, p.y, p.z, count, spread, spread, spread, 0.02);
    }

    public static void halloween(ServerLevel level, Vec3 p) {
        level.sendParticles(ModParticles.HALLOWEEN.get(), p.x, p.y, p.z, 1, 0.2, 0.1, 0.2, 0.0);
    }

    /** Earth thrown up where something bursts out of (or dives into) the ground. */
    public static void clods(ServerLevel level, Vec3 p, int count, double speed) {
        level.sendParticles(ModParticles.CLOD.get(), p.x, p.y + 0.1, p.z, count, 0.3, 0.05, 0.3, speed);
    }

    private Fx() {
    }
}
