package com.csm.hybrids.registry;

import com.csm.hybrids.CsmMod;
import com.csm.hybrids.effect.HalloweenEffect;
import net.minecraft.world.effect.MobEffect;
import net.minecraftforge.registries.DeferredRegister;
import net.minecraftforge.registries.ForgeRegistries;
import net.minecraftforge.registries.RegistryObject;

public final class ModEffects {
    public static final DeferredRegister<MobEffect> EFFECTS = DeferredRegister.create(ForgeRegistries.MOB_EFFECTS, CsmMod.MODID);

    /** Cosmo's Total Understanding: the whole universe at once. The victim can only think "Halloween". */
    public static final RegistryObject<MobEffect> HALLOWEEN = EFFECTS.register("halloween", HalloweenEffect::new);
    /** The Darkness Devil's wounds: nothing heals while it lasts. */
    public static final RegistryObject<MobEffect> UNHEALING = EFFECTS.register("unhealing",
            () -> new com.csm.hybrids.effect.DevilWoundEffect(0x2A1A3A, false));
    /** Both arms sheared off by the Darkness Devil. */
    public static final RegistryObject<MobEffect> SEVERED = EFFECTS.register("severed",
            () -> new com.csm.hybrids.effect.DevilWoundEffect(0x6A0A0A, true));

    private ModEffects() {
    }
}
