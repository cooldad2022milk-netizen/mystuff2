package com.csm.hybrids.registry;

import com.csm.hybrids.CsmMod;
import net.minecraft.core.registries.Registries;
import net.minecraft.network.chat.Component;
import net.minecraft.world.item.CreativeModeTab;
import net.minecraft.world.item.ItemStack;
import net.minecraftforge.registries.DeferredRegister;
import net.minecraftforge.registries.RegistryObject;

public final class ModTabs {
    public static final DeferredRegister<CreativeModeTab> TABS = DeferredRegister.create(Registries.CREATIVE_MODE_TAB, CsmMod.MODID);

    public static final RegistryObject<CreativeModeTab> MAIN = TABS.register("main", () -> CreativeModeTab.builder()
            .title(Component.translatable("itemGroup.csm"))
            .icon(() -> new ItemStack(ModItems.CHAINSAW_DEVIL_HEART.get()))
            .displayItems((params, out) -> {
                out.accept(ModItems.CHAINSAW_DEVIL_HEART.get());
                out.accept(ModItems.CROSSBOW_DEVIL_HEART.get());
                out.accept(ModItems.FLAMETHROWER_DEVIL_HEART.get());
                out.accept(ModItems.WHIP_DEVIL_HEART.get());
                out.accept(ModItems.BOMB_DEVIL_HEART.get());
                out.accept(ModItems.SPEAR_DEVIL_HEART.get());
                out.accept(ModItems.KATANA_DEVIL_HEART.get());
                out.accept(ModItems.LONGSWORD_DEVIL_HEART.get());
                out.accept(ModItems.BLOOD_DEVIL_REMAINS.get());
                out.accept(ModItems.SHARK_DEVIL_REMAINS.get());
                out.accept(ModItems.VIOLENCE_DEVIL_REMAINS.get());
                out.accept(ModItems.COSMOS_DEVIL_REMAINS.get());
                out.accept(ModItems.GUN_DEVIL_FLESH.get());
                out.accept(ModItems.HUMAN_HEART.get());
                out.accept(ModItems.BLOOD_VIAL.get());
                ModItems.ESSENCES.values().forEach(e -> out.accept(e.get()));
                ModItems.SPAWN_EGGS.values().forEach(e -> out.accept(e.get()));
            })
            .build());

    private ModTabs() {
    }
}
