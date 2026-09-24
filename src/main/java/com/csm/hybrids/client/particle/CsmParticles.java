package com.csm.hybrids.client.particle;

import com.csm.hybrids.registry.ModParticles;
import com.mojang.blaze3d.platform.GlStateManager;
import com.mojang.blaze3d.systems.RenderSystem;
import com.mojang.blaze3d.vertex.BufferBuilder;
import com.mojang.blaze3d.vertex.DefaultVertexFormat;
import com.mojang.blaze3d.vertex.Tesselator;
import com.mojang.blaze3d.vertex.VertexConsumer;
import com.mojang.blaze3d.vertex.VertexFormat;
import net.minecraft.client.Camera;
import net.minecraft.client.multiplayer.ClientLevel;
import net.minecraft.client.particle.ParticleRenderType;
import net.minecraft.client.particle.SpriteSet;
import net.minecraft.client.particle.TextureSheetParticle;
import net.minecraft.client.renderer.texture.TextureAtlas;
import net.minecraft.client.renderer.texture.TextureManager;
import net.minecraft.util.Mth;
import net.minecraft.world.phys.Vec3;
import net.minecraftforge.client.event.RegisterParticleProvidersEvent;
import org.joml.Vector3f;

/**
 * All of the mod's particles. None of them use vanilla particle art or behaviour.
 */
public final class CsmParticles {
    private static final int FULL_BRIGHT = 0xF000F0;

    /** Glow blending for fire, sparks, embers and energy. */
    public static final ParticleRenderType ADDITIVE = new ParticleRenderType() {
        @Override
        public void begin(BufferBuilder builder, TextureManager textures) {
            RenderSystem.depthMask(false);
            RenderSystem.setShaderTexture(0, TextureAtlas.LOCATION_PARTICLES);
            RenderSystem.enableBlend();
            RenderSystem.blendFunc(GlStateManager.SourceFactor.SRC_ALPHA, GlStateManager.DestFactor.ONE);
            builder.begin(VertexFormat.Mode.QUADS, DefaultVertexFormat.PARTICLE);
        }

        @Override
        public void end(Tesselator tesselator) {
            tesselator.end();
            RenderSystem.defaultBlendFunc();
            RenderSystem.depthMask(true);
        }

        @Override
        public String toString() {
            return "CSM_ADDITIVE";
        }
    };

    public static void register(RegisterParticleProvidersEvent event) {
        event.registerSpriteSet(ModParticles.BLOOD.get(), s -> (t, l, x, y, z, vx, vy, vz) -> new Blood(l, x, y, z, vx, vy, vz, s));
        event.registerSpriteSet(ModParticles.BLOOD_MIST.get(), s -> (t, l, x, y, z, vx, vy, vz) -> new Puff(l, x, y, z, vx, vy, vz, s, Puff.MIST));
        event.registerSpriteSet(ModParticles.SMOKE.get(), s -> (t, l, x, y, z, vx, vy, vz) -> new Puff(l, x, y, z, vx, vy, vz, s, Puff.SMOKE));
        event.registerSpriteSet(ModParticles.EXHAUST.get(), s -> (t, l, x, y, z, vx, vy, vz) -> new Puff(l, x, y, z, vx, vy, vz, s, Puff.EXHAUST));
        event.registerSpriteSet(ModParticles.GORE.get(), s -> (t, l, x, y, z, vx, vy, vz) -> new Chunk(l, x, y, z, vx, vy, vz, s, false));
        event.registerSpriteSet(ModParticles.SHARD.get(), s -> (t, l, x, y, z, vx, vy, vz) -> new Chunk(l, x, y, z, vx, vy, vz, s, true));
        event.registerSpriteSet(ModParticles.SPARK.get(), s -> (t, l, x, y, z, vx, vy, vz) -> new Spark(l, x, y, z, vx, vy, vz, s));
        event.registerSpriteSet(ModParticles.FIRE.get(), s -> (t, l, x, y, z, vx, vy, vz) -> new Fire(l, x, y, z, vx, vy, vz, s));
        event.registerSpriteSet(ModParticles.EMBER.get(), s -> (t, l, x, y, z, vx, vy, vz) -> new Ember(l, x, y, z, vx, vy, vz, s));
        event.registerSpriteSet(ModParticles.CHARGE.get(), s -> (t, l, x, y, z, vx, vy, vz) -> new Charge(l, x, y, z, vx, vy, vz, s));
        event.registerSpriteSet(ModParticles.SLASH.get(), s -> (t, l, x, y, z, vx, vy, vz) -> new Slash(l, x, y, z, vx, vy, vz, s));
        event.registerSpriteSet(ModParticles.SHOCKWAVE.get(), s -> (t, l, x, y, z, vx, vy, vz) -> new Shockwave(l, x, y, z, vx, vy, s));
        event.registerSpriteSet(ModParticles.SPEED_LINE.get(), s -> (t, l, x, y, z, vx, vy, vz) -> new SpeedLine(l, x, y, z, vx, vy, vz, s));
        event.registerSpriteSet(ModParticles.WHIP_TRAIL.get(), s -> (t, l, x, y, z, vx, vy, vz) ->
                new SpeedLine(l, x, y, z, vx, vy, vz, s, 1.0f, 0.5f, 0.4f, 0.035f, 5));
        event.registerSpriteSet(ModParticles.IMPACT.get(), s -> (t, l, x, y, z, vx, vy, vz) -> new Impact(l, x, y, z, vx, s));
        event.registerSpriteSet(ModParticles.BLAST.get(), s -> (t, l, x, y, z, vx, vy, vz) -> new Fireball(l, x, y, z, vx, s));
        event.registerSpriteSet(ModParticles.BULLET.get(), s -> (t, l, x, y, z, vx, vy, vz) ->
                new SpeedLine(l, x, y, z, vx, vy, vz, s, 1.0f, 0.85f, 0.45f, 0.022f, 3));
        event.registerSpriteSet(ModParticles.HALLOWEEN.get(), s -> (t, l, x, y, z, vx, vy, vz) -> new Word(l, x, y, z, s));
        event.registerSpriteSet(ModParticles.STAR.get(), s -> (t, l, x, y, z, vx, vy, vz) -> new Star(l, x, y, z, vx, vy, vz, s));
        event.registerSpriteSet(ModParticles.CLOD.get(), s -> (t, l, x, y, z, vx, vy, vz) -> new Chunk(l, x, y, z, vx, vy, vz, s, false));
        event.registerSpriteSet(ModParticles.CHAIN.get(), s -> (t, l, x, y, z, vx, vy, vz) -> new ChainLine(l, x, y, z, vx, vy, vz, s));
    }

    // =============================================================================== helpers
    /** Draws a textured quad around {@code c} spanned by half-axes {@code u} and {@code v} (both faces). */
    static void quad(VertexConsumer b, Vector3f c, Vector3f u, Vector3f v, float u0, float u1, float v0, float v1,
                     float r, float g, float bl, float a, int light, boolean doubleSided) {
        float[][] corners = {{-1, -1}, {-1, 1}, {1, 1}, {1, -1}};
        float[][] uvs = {{u0, v1}, {u0, v0}, {u1, v0}, {u1, v1}};
        for (int i = 0; i < 4; i++) {
            vert(b, c, u, v, corners[i], uvs[i], r, g, bl, a, light);
        }
        if (doubleSided) {
            for (int i = 3; i >= 0; i--) {
                vert(b, c, u, v, corners[i], uvs[i], r, g, bl, a, light);
            }
        }
    }

    private static void vert(VertexConsumer b, Vector3f c, Vector3f u, Vector3f v, float[] k, float[] uv,
                             float r, float g, float bl, float a, int light) {
        b.vertex(c.x + u.x * k[0] + v.x * k[1], c.y + u.y * k[0] + v.y * k[1], c.z + u.z * k[0] + v.z * k[1])
                .uv(uv[0], uv[1]).color(r, g, bl, a).uv2(light).endVertex();
    }

    static Vector3f camRel(TextureSheetParticle p, double x, double y, double z, Camera cam) {
        Vec3 c = cam.getPosition();
        return new Vector3f((float) (x - c.x), (float) (y - c.y), (float) (z - c.z));
    }

    // =============================================================================== blood
    /** Glossy drops that arc, fall, and flatten into a splat. */
    public static class Blood extends TextureSheetParticle {
        private final SpriteSet sprites;
        private boolean splat;

        Blood(ClientLevel level, double x, double y, double z, double vx, double vy, double vz, SpriteSet sprites) {
            super(level, x, y, z);
            this.sprites = sprites;
            this.xd = vx + (random.nextDouble() - 0.5) * 0.06;
            this.yd = vy + random.nextDouble() * 0.1;
            this.zd = vz + (random.nextDouble() - 0.5) * 0.06;
            this.gravity = 1.0f;
            this.friction = 0.97f;
            this.lifetime = 40 + random.nextInt(40);
            this.quadSize = 0.02f + random.nextFloat() * 0.035f;
            this.hasPhysics = true;
            setSprite(sprites.get(random.nextInt(3), 3));
        }

        @Override
        public void tick() {
            super.tick();
            if (onGround && !splat) {
                splat = true;
                setSprite(sprites.get(3, 3));
                quadSize *= 2.2f;
                lifetime = Math.min(lifetime, age + 60);
            }
            if (splat) {
                xd = zd = 0;
                alpha = Math.min(1f, (lifetime - age) / 25f);
            }
        }

        @Override
        public ParticleRenderType getRenderType() {
            return ParticleRenderType.PARTICLE_SHEET_TRANSLUCENT;
        }
    }

    // =============================================================================== puffs (mist, smoke, exhaust)
    public static class Puff extends TextureSheetParticle {
        static final int MIST = 0;
        static final int SMOKE = 1;
        static final int EXHAUST = 2;
        private final SpriteSet sprites;
        private final int kind;
        private final float startSize;

        Puff(ClientLevel level, double x, double y, double z, double vx, double vy, double vz, SpriteSet sprites, int kind) {
            super(level, x, y, z);
            this.sprites = sprites;
            this.kind = kind;
            this.xd = vx;
            this.yd = vy + (kind == MIST ? 0 : 0.015 + random.nextDouble() * 0.02);
            this.zd = vz;
            this.friction = 0.9f;
            this.gravity = kind == MIST ? 0.02f : -0.01f;
            this.lifetime = switch (kind) {
                case MIST -> 14 + random.nextInt(10);
                case EXHAUST -> 18 + random.nextInt(12);
                default -> 40 + random.nextInt(30);
            };
            this.startSize = switch (kind) {
                case MIST -> 0.18f + random.nextFloat() * 0.15f;
                case EXHAUST -> 0.12f + random.nextFloat() * 0.1f;
                default -> 0.22f + random.nextFloat() * 0.25f;
            };
            this.quadSize = startSize;
            this.roll = this.oRoll = random.nextFloat() * Mth.TWO_PI;
            this.alpha = kind == SMOKE ? 0.6f : 0.55f;
            setSpriteFromAge(sprites);
        }

        @Override
        public void tick() {
            super.tick();
            if (!removed) {
                setSpriteFromAge(sprites);
                float f = age / (float) lifetime;
                quadSize = startSize * (1f + f * (kind == SMOKE ? 1.7f : 1.5f));
                alpha = (kind == SMOKE ? 0.6f : 0.55f) * (1f - f * f);
                oRoll = roll;
                roll += 0.02f;
            }
        }

        @Override
        public ParticleRenderType getRenderType() {
            return ParticleRenderType.PARTICLE_SHEET_TRANSLUCENT;
        }
    }

    // =============================================================================== chunks (gore, shards)
    public static class Chunk extends TextureSheetParticle {
        private final float spin;
        private final boolean metal;

        Chunk(ClientLevel level, double x, double y, double z, double vx, double vy, double vz, SpriteSet sprites, boolean metal) {
            super(level, x, y, z);
            this.metal = metal;
            this.xd = vx;
            this.yd = vy + 0.15 + random.nextDouble() * 0.15;
            this.zd = vz;
            this.gravity = 1.1f;
            this.friction = 0.98f;
            this.lifetime = 40 + random.nextInt(40);
            this.quadSize = (metal ? 0.06f : 0.08f) + random.nextFloat() * 0.06f;
            this.hasPhysics = true;
            this.spin = (random.nextFloat() - 0.5f) * 0.6f;
            pickSprite(sprites);
        }

        @Override
        public void tick() {
            super.tick();
            oRoll = roll;
            if (!onGround) {
                roll += spin;
            } else {
                xd *= 0.6;
                zd *= 0.6;
            }
            if (age > lifetime - 15) {
                alpha = (lifetime - age) / 15f;
            }
        }

        @Override
        public ParticleRenderType getRenderType() {
            return ParticleRenderType.PARTICLE_SHEET_TRANSLUCENT;
        }

        @Override
        protected int getLightColor(float partialTick) {
            return metal ? Math.max(super.getLightColor(partialTick), 0xA000A0) : super.getLightColor(partialTick);
        }
    }

    // =============================================================================== sparks
    /** Hot metal sparks, drawn as streaks along their velocity. */
    public static class Spark extends TextureSheetParticle {
        Spark(ClientLevel level, double x, double y, double z, double vx, double vy, double vz, SpriteSet sprites) {
            super(level, x, y, z);
            this.xd = vx;
            this.yd = vy;
            this.zd = vz;
            this.gravity = 0.7f;
            this.friction = 0.94f;
            this.lifetime = 8 + random.nextInt(10);
            this.quadSize = 0.012f + random.nextFloat() * 0.012f;
            this.hasPhysics = true;
            pickSprite(sprites);
        }

        @Override
        public void tick() {
            super.tick();
            float f = age / (float) lifetime;
            gCol = 1f - f * 0.6f;
            bCol = 1f - f;
            if (onGround) {
                yd = -yd * 0.4;
            }
        }

        @Override
        public void render(VertexConsumer b, Camera cam, float pt) {
            Vector3f c = camRel(this, Mth.lerp(pt, xo, x), Mth.lerp(pt, yo, y), Mth.lerp(pt, zo, z), cam);
            Vector3f vel = new Vector3f((float) xd, (float) yd, (float) zd);
            float len = Math.min(Math.max(vel.length() * 0.9f, quadSize * 2f), 0.3f);
            if (vel.lengthSquared() < 1e-6f) {
                vel.set(0, 1, 0);
            }
            Vector3f along = new Vector3f(vel).normalize(len);
            Vector3f side = new Vector3f(vel).cross(c).normalize(quadSize);
            if (!Float.isFinite(side.x)) {
                side.set(quadSize, 0, 0);
            }
            quad(b, c, side, along, getU0(), getU1(), getV0(), getV1(), rCol, gCol, bCol, 1f - age / (float) lifetime,
                    FULL_BRIGHT, false);
        }

        @Override
        public ParticleRenderType getRenderType() {
            return ADDITIVE;
        }
    }

    // =============================================================================== fire
    public static class Fire extends TextureSheetParticle {
        private final SpriteSet sprites;
        private final float startSize;

        Fire(ClientLevel level, double x, double y, double z, double vx, double vy, double vz, SpriteSet sprites) {
            super(level, x, y, z);
            this.sprites = sprites;
            this.xd = vx;
            this.yd = vy;
            this.zd = vz;
            this.friction = 0.9f;
            this.gravity = -0.03f;
            this.lifetime = 12 + random.nextInt(10);
            this.startSize = 0.18f + random.nextFloat() * 0.18f;
            this.quadSize = startSize;
            this.hasPhysics = false;
            setSpriteFromAge(sprites);
        }

        @Override
        public void tick() {
            super.tick();
            if (!removed) {
                setSpriteFromAge(sprites);
                float f = age / (float) lifetime;
                quadSize = startSize * (0.7f + 1.4f * f - 0.8f * f * f);
                alpha = 1f - f * f;
                yd += 0.004;
            }
        }

        @Override
        protected int getLightColor(float partialTick) {
            return FULL_BRIGHT;
        }

        @Override
        public ParticleRenderType getRenderType() {
            return ADDITIVE;
        }
    }

    public static class Ember extends TextureSheetParticle {
        Ember(ClientLevel level, double x, double y, double z, double vx, double vy, double vz, SpriteSet sprites) {
            super(level, x, y, z);
            this.xd = vx;
            this.yd = vy + 0.02;
            this.zd = vz;
            this.friction = 0.96f;
            this.gravity = -0.02f;
            this.lifetime = 25 + random.nextInt(30);
            this.quadSize = 0.025f + random.nextFloat() * 0.03f;
            pickSprite(sprites);
        }

        @Override
        public void tick() {
            super.tick();
            xd += (random.nextDouble() - 0.5) * 0.01;
            zd += (random.nextDouble() - 0.5) * 0.01;
            alpha = (1f - age / (float) lifetime) * (0.6f + random.nextFloat() * 0.4f);
        }

        @Override
        protected int getLightColor(float partialTick) {
            return FULL_BRIGHT;
        }

        @Override
        public ParticleRenderType getRenderType() {
            return ADDITIVE;
        }
    }

    public static class Charge extends TextureSheetParticle {
        Charge(ClientLevel level, double x, double y, double z, double vx, double vy, double vz, SpriteSet sprites) {
            super(level, x, y, z);
            this.xd = vx;
            this.yd = vy;
            this.zd = vz;
            this.friction = 1f;
            this.lifetime = 8;
            this.quadSize = 0.08f;
            pickSprite(sprites);
        }

        @Override
        public void tick() {
            super.tick();
            quadSize = 0.08f * (1f - age / (float) lifetime * 0.7f);
        }

        @Override
        protected int getLightColor(float partialTick) {
            return FULL_BRIGHT;
        }

        @Override
        public ParticleRenderType getRenderType() {
            return ADDITIVE;
        }
    }

    /** Cosmos sparkle: twinkles and drifts, additive. */
    public static class Star extends TextureSheetParticle {
        private final float base;

        Star(ClientLevel level, double x, double y, double z, double vx, double vy, double vz, SpriteSet sprites) {
            super(level, x, y, z);
            this.xd = vx;
            this.yd = vy;
            this.zd = vz;
            this.friction = 0.92f;
            this.gravity = 0;
            this.lifetime = 16 + random.nextInt(16);
            this.base = 0.05f + random.nextFloat() * 0.07f;
            this.quadSize = base;
            this.roll = this.oRoll = random.nextFloat() * Mth.TWO_PI;
            float hue = random.nextFloat();
            // pink / violet / pale gold / white
            if (hue < 0.35f) {
                setColor(1f, 0.55f, 0.85f);
            } else if (hue < 0.6f) {
                setColor(0.7f, 0.55f, 1f);
            } else if (hue < 0.8f) {
                setColor(1f, 0.9f, 0.6f);
            }
            pickSprite(sprites);
        }

        @Override
        public void tick() {
            super.tick();
            float f = age / (float) lifetime;
            quadSize = base * (0.6f + 0.6f * Mth.abs(Mth.sin(age * 0.7f))) * (1f - f * 0.5f);
            alpha = 1f - f * f;
        }

        @Override
        protected int getLightColor(float partialTick) {
            return FULL_BRIGHT;
        }

        @Override
        public ParticleRenderType getRenderType() {
            return ADDITIVE;
        }
    }

    /** A word drifting up out of a victim's head ("Halloween"): a camera-facing sprite that fades out. */
    public static class Word extends TextureSheetParticle {
        Word(ClientLevel level, double x, double y, double z, SpriteSet sprites) {
            super(level, x, y, z);
            this.xd = (random.nextDouble() - 0.5) * 0.01;
            this.yd = 0.025;
            this.zd = (random.nextDouble() - 0.5) * 0.01;
            this.friction = 0.96f;
            this.gravity = 0;
            this.lifetime = 34;
            this.quadSize = 0.32f;
            this.roll = this.oRoll = (random.nextFloat() - 0.5f) * 0.4f;
            pickSprite(sprites);
        }

        @Override
        public void tick() {
            super.tick();
            float f = age / (float) lifetime;
            alpha = f < 0.2f ? f / 0.2f : 1f - (f - 0.2f) / 0.8f;
            quadSize = 0.32f + f * 0.1f;
        }

        @Override
        protected int getLightColor(float partialTick) {
            return FULL_BRIGHT;
        }

        @Override
        public ParticleRenderType getRenderType() {
            return ParticleRenderType.PARTICLE_SHEET_TRANSLUCENT;
        }
    }

    // =============================================================================== oriented effects
    /** Chainsaw cut crescent lying in the swing plane, facing the spawn vector. */
    public static class Slash extends TextureSheetParticle {
        private final SpriteSet sprites;
        private final Vector3f fwd;
        private final Vector3f right;
        private final float size;

        Slash(ClientLevel level, double x, double y, double z, double vx, double vy, double vz, SpriteSet sprites) {
            super(level, x, y, z);
            this.sprites = sprites;
            this.xd = this.yd = this.zd = 0;
            this.gravity = 0;
            this.lifetime = 7;
            Vector3f f = new Vector3f((float) vx, (float) vy, (float) vz);
            this.size = Math.max(0.5f, f.length());
            f.normalize();
            Vector3f r = new Vector3f(f).cross(0, 1, 0);
            if (r.lengthSquared() < 1e-4f) {
                r.set(1, 0, 0);
            }
            r.normalize();
            // random tilt about the facing axis keeps consecutive cuts from looking identical
            float tilt = (random.nextFloat() - 0.5f) * 0.9f;
            Vector3f up = new Vector3f(r).cross(f).normalize();
            this.right = new Vector3f(r).mul(Mth.cos(tilt)).add(new Vector3f(up).mul(Mth.sin(tilt)));
            if (random.nextBoolean()) {
                this.right.negate();
            }
            this.fwd = f;
            setSpriteFromAge(sprites);
        }

        @Override
        public void tick() {
            super.tick();
            if (!removed) {
                setSpriteFromAge(sprites);
            }
        }

        @Override
        public void render(VertexConsumer b, Camera cam, float pt) {
            Vector3f c = camRel(this, x, y, z, cam);
            float grow = Math.min(1f, (age + pt) / 3f) * 0.3f + 0.7f;
            Vector3f u = new Vector3f(right).mul(size * grow);
            Vector3f v = new Vector3f(fwd).mul(size * grow);
            quad(b, c, u, v, getU0(), getU1(), getV0(), getV1(), 1f, 1f, 1f, 1f, FULL_BRIGHT, true);
        }

        @Override
        public ParticleRenderType getRenderType() {
            return ParticleRenderType.PARTICLE_SHEET_TRANSLUCENT;
        }
    }

    /** Ring that races outward along the ground. */
    public static class Shockwave extends TextureSheetParticle {
        private final float radius;
        private final boolean glow;

        Shockwave(ClientLevel level, double x, double y, double z, double radius, double variant, SpriteSet sprites) {
            super(level, x, y, z);
            this.xd = this.yd = this.zd = 0;
            this.gravity = 0;
            this.radius = (float) Math.max(0.5, radius);
            this.lifetime = 10 + (int) (radius * 1.2);
            this.glow = (int) Math.round(variant) == 0;
            switch ((int) Math.round(variant)) {
                case 1 -> setColor(0.85f, 0.08f, 0.1f);
                case 2 -> setColor(0.8f, 0.85f, 1f);
                default -> setColor(1f, 0.55f, 0.15f);
            }
            pickSprite(sprites);
        }

        @Override
        public void render(VertexConsumer b, Camera cam, float pt) {
            Vector3f c = camRel(this, x, y, z, cam);
            float f = Math.min(1f, (age + pt) / lifetime);
            float r = radius * (1f - (1f - f) * (1f - f));
            float a = 1f - f;
            quad(b, c, new Vector3f(r, 0, 0), new Vector3f(0, 0, r), getU0(), getU1(), getV0(), getV1(), rCol, gCol,
                    bCol, a, FULL_BRIGHT, true);
        }

        @Override
        public ParticleRenderType getRenderType() {
            return glow ? ADDITIVE : ParticleRenderType.PARTICLE_SHEET_TRANSLUCENT;
        }
    }

    /** Streak from the spawn point along the given vector (after-images, bolt trails). */
    public static class SpeedLine extends TextureSheetParticle {
        private final Vector3f vec;

        SpeedLine(ClientLevel level, double x, double y, double z, double vx, double vy, double vz, SpriteSet sprites) {
            this(level, x, y, z, vx, vy, vz, sprites, 1f, 1f, 1f, -1f, 7);
        }

        /** @param size half-width of the streak; negative = random 0.06-0.12 */
        SpeedLine(ClientLevel level, double x, double y, double z, double vx, double vy, double vz, SpriteSet sprites,
                  float r, float g, float b, float size, int life) {
            super(level, x, y, z);
            this.vec = new Vector3f((float) vx, (float) vy, (float) vz);
            this.xd = this.yd = this.zd = 0;
            this.gravity = 0;
            this.lifetime = life;
            this.quadSize = size > 0 ? size * (0.8f + random.nextFloat() * 0.4f) : 0.06f + random.nextFloat() * 0.06f;
            setColor(r, g, b);
            pickSprite(sprites);
        }

        @Override
        public void render(VertexConsumer b, Camera cam, float pt) {
            Vector3f start = camRel(this, x, y, z, cam);
            Vector3f half = new Vector3f(vec).mul(0.5f);
            Vector3f c = new Vector3f(start).add(half);
            Vector3f side = new Vector3f(vec).cross(c);
            if (side.lengthSquared() < 1e-6f) {
                side.set(0, 1, 0);
            }
            side.normalize(quadSize);
            // a streak that runs through (or right past) the viewer would fill the screen as a slab: fade it out
            float t = vec.lengthSquared() < 1e-6f ? 0f : Mth.clamp(-start.dot(vec) / vec.lengthSquared(), 0f, 1f);
            float near = new Vector3f(vec).mul(t).add(start).length();
            float fade = Mth.clamp((near - 0.9f) / 1.6f, 0f, 1f);
            float a = (1f - (age + pt) / lifetime) * fade;
            if (a <= 0.01f) {
                return;
            }
            quad(b, c, half, side, getU0(), getU1(), getV0(), getV1(), rCol, gCol, bCol, a, FULL_BRIGHT, true);
        }

        @Override
        public ParticleRenderType getRenderType() {
            return ADDITIVE;
        }
    }

    /**
     * A taut chain: a row of alternating links (face-on, then edge-on) running from the spawn point along its vector,
     * lit like the world around it. Several spawned at once on the same spot stay up longer (they are identical).
     */
    public static class ChainLine extends TextureSheetParticle {
        private final Vector3f vec;

        ChainLine(ClientLevel level, double x, double y, double z, double vx, double vy, double vz, SpriteSet sprites) {
            super(level, x, y, z);
            this.vec = new Vector3f((float) vx, (float) vy, (float) vz);
            this.xd = this.yd = this.zd = 0;
            this.gravity = 0;
            this.lifetime = 10 + random.nextInt(24);
            this.quadSize = 0.11f;
            pickSprite(sprites);
        }

        @Override
        public void render(VertexConsumer b, Camera cam, float pt) {
            Vector3f start = camRel(this, x, y, z, cam);
            float len = vec.length();
            if (len < 1e-3f) {
                return;
            }
            int links = Math.max(1, (int) (len / 0.2f));
            Vector3f step = new Vector3f(vec).div(links);
            Vector3f half = new Vector3f(step).mul(0.62f);
            Vector3f side = new Vector3f(vec).cross(0, 1, 0);
            if (side.lengthSquared() < 1e-6f) {
                side.set(1, 0, 0);
            }
            side.normalize(quadSize);
            Vector3f side2 = new Vector3f(vec).cross(side).normalize(quadSize);
            // shaking taut while it binds
            float shake = (float) Math.sin((age + pt) * 2.1f) * 0.02f;
            int light = getLightColor(pt);
            float a = Mth.clamp((lifetime - age - pt) / 4f, 0f, 1f);
            for (int i = 0; i < links; i++) {
                Vector3f c = new Vector3f(step).mul(i + 0.5f).add(start).add(0, shake * (i % 2 == 0 ? 1 : -1), 0);
                quad(b, c, half, i % 2 == 0 ? side : side2, getU0(), getU1(), getV0(), getV1(), 0.85f, 0.85f, 0.9f, a,
                        light, true);
            }
        }

        @Override
        public ParticleRenderType getRenderType() {
            return ParticleRenderType.PARTICLE_SHEET_TRANSLUCENT;
        }
    }

    /** Manga impact burst: spiky black flash that punches out and fades. */
    public static class Impact extends TextureSheetParticle {
        private final SpriteSet sprites;
        private final float size;

        Impact(ClientLevel level, double x, double y, double z, double size, SpriteSet sprites) {
            super(level, x, y, z);
            this.sprites = sprites;
            this.size = (float) Math.max(0.4, size);
            this.xd = this.yd = this.zd = 0;
            this.gravity = 0;
            this.lifetime = 6;
            this.roll = this.oRoll = random.nextFloat() * Mth.TWO_PI;
            setSpriteFromAge(sprites);
        }

        @Override
        public void tick() {
            super.tick();
            if (!removed) {
                setSpriteFromAge(sprites);
                float f = age / (float) lifetime;
                quadSize = size * (0.6f + 0.6f * f);
                alpha = 1f - f * f;
            }
        }

        @Override
        protected int getLightColor(float partialTick) {
            return FULL_BRIGHT;
        }

        @Override
        public ParticleRenderType getRenderType() {
            return ParticleRenderType.PARTICLE_SHEET_TRANSLUCENT;
        }
    }

    /** Bomb Devil fireball: a white-hot core that blooms out, turns orange-red and rolls upward. */
    public static class Fireball extends TextureSheetParticle {
        private final SpriteSet sprites;
        private final float size;

        Fireball(ClientLevel level, double x, double y, double z, double size, SpriteSet sprites) {
            super(level, x, y, z);
            this.sprites = sprites;
            this.size = (float) Math.max(0.3, size);
            this.xd = this.zd = 0;
            this.yd = 0.02;
            this.gravity = -0.01f;
            this.friction = 0.9f;
            this.lifetime = 12 + random.nextInt(4);
            this.roll = this.oRoll = random.nextFloat() * Mth.TWO_PI;
            setSpriteFromAge(sprites);
        }

        @Override
        public void render(VertexConsumer buffer, Camera cam, float partialTick) {
            // a fireball going off in your face would white out the screen: thin it out around the camera
            Vec3 c = cam.getPosition();
            double d = Math.sqrt((x - c.x) * (x - c.x) + (y - c.y) * (y - c.y) + (z - c.z) * (z - c.z));
            float keep = Mth.clamp((float) ((d - quadSize * 0.2) / (quadSize * 1.1)), 0.2f, 1f);
            float a = alpha;
            alpha = a * keep;
            super.render(buffer, cam, partialTick);
            alpha = a;
        }

        @Override
        public void tick() {
            super.tick();
            if (!removed) {
                setSpriteFromAge(sprites);
                float f = age / (float) lifetime;
                quadSize = size * (0.35f + 1.0f * (1f - (1f - f) * (1f - f)));
                alpha = f < 0.6f ? 1f : 1f - (f - 0.6f) / 0.4f;
            }
        }

        @Override
        protected int getLightColor(float partialTick) {
            return FULL_BRIGHT;
        }

        @Override
        public ParticleRenderType getRenderType() {
            return ADDITIVE;
        }
    }

    private CsmParticles() {
    }
}
