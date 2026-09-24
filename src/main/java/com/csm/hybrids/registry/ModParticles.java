package com.csm.hybrids.registry;

import com.csm.hybrids.CsmMod;
import net.minecraft.core.particles.ParticleType;
import net.minecraft.core.particles.SimpleParticleType;
import net.minecraftforge.registries.DeferredRegister;
import net.minecraftforge.registries.ForgeRegistries;
import net.minecraftforge.registries.RegistryObject;

/**
 * Every particle the mod shows is one of these (no vanilla particles).
 * Some read their spawn "velocity" as parameters instead of motion - see {@link com.csm.hybrids.fx.Fx}.
 */
public final class ModParticles {
    public static final DeferredRegister<ParticleType<?>> PARTICLES = DeferredRegister.create(ForgeRegistries.PARTICLE_TYPES, CsmMod.MODID);

    /** Heavy blood drops: arc, fall and splat on the ground. */
    public static final RegistryObject<SimpleParticleType> BLOOD = reg("blood", false);
    /** Fine red spray that hangs in the air. */
    public static final RegistryObject<SimpleParticleType> BLOOD_MIST = reg("blood_mist", false);
    /** Tumbling chunks of flesh. */
    public static final RegistryObject<SimpleParticleType> GORE = reg("gore", false);
    /** White-hot metal sparks from the saw chains (stretched along their motion). */
    public static final RegistryObject<SimpleParticleType> SPARK = reg("spark", false);
    /** Chainsaw cut crescent. Velocity = facing direction, its length = size in blocks. */
    public static final RegistryObject<SimpleParticleType> SLASH = reg("slash", true);
    /** Two-stroke exhaust smoke from the Chainsaw Devil's engine. */
    public static final RegistryObject<SimpleParticleType> EXHAUST = reg("exhaust", false);
    /** Custom animated flame. */
    public static final RegistryObject<SimpleParticleType> FIRE = reg("fire", false);
    /** Glowing embers drifting up. */
    public static final RegistryObject<SimpleParticleType> EMBER = reg("ember", false);
    /** Thick dark smoke. */
    public static final RegistryObject<SimpleParticleType> SMOKE = reg("smoke", false);
    /** The Octopus Devil's ink: big black clouds that hang in the air. */
    public static final RegistryObject<SimpleParticleType> INK = reg("ink", false);
    /** Flat ring on the ground. Velocity x = radius, y = colour variant (0 fire, 1 blood, 2 steel). */
    public static final RegistryObject<SimpleParticleType> SHOCKWAVE = reg("shockwave", true);
    /** Speed streak. Velocity = the streak vector (from spawn point). */
    public static final RegistryObject<SimpleParticleType> SPEED_LINE = reg("speed_line", true);
    /** Coral streak of a cracking whip. Velocity = the streak vector (from spawn point). */
    public static final RegistryObject<SimpleParticleType> WHIP_TRAIL = reg("whip_trail", true);
    /** Manga-style impact burst. Velocity x = size. */
    public static final RegistryObject<SimpleParticleType> IMPACT = reg("impact", true);
    /** Steel shards (crossbow). */
    public static final RegistryObject<SimpleParticleType> SHARD = reg("shard", false);
    /** Bomb Devil fireball bloom. Velocity x = size. */
    public static final RegistryObject<SimpleParticleType> BLAST = reg("blast", true);
    /** Bullet tracer. Velocity = the streak vector (from muzzle to impact). */
    public static final RegistryObject<SimpleParticleType> BULLET = reg("bullet", true);
    /** Cosmo's word, drifting up out of a victim's head. */
    public static final RegistryObject<SimpleParticleType> HALLOWEEN = reg("halloween", true);
    /** Cosmos sparkle (additive, twinkles). */
    public static final RegistryObject<SimpleParticleType> STAR = reg("star", false);
    /** Clods of earth thrown up by Beam swimming through the ground. */
    public static final RegistryObject<SimpleParticleType> CLOD = reg("clod", false);
    /** A chain lashing out (Makima). Velocity = the chain vector (from spawn point); drawn as a row of links. */
    public static final RegistryObject<SimpleParticleType> CHAIN = reg("chain", true);
    /** Crimson charge motes gathering on the overdrawn crossbow. */
    public static final RegistryObject<SimpleParticleType> CHARGE = reg("charge", false);

    private static RegistryObject<SimpleParticleType> reg(String name, boolean alwaysShow) {
        return PARTICLES.register(name, () -> new SimpleParticleType(alwaysShow));
    }

    private ModParticles() {
    }
}
