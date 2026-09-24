package com.csm.hybrids.client;

import com.csm.hybrids.CsmMod;
import com.csm.hybrids.ability.Ability;
import com.csm.hybrids.contract.Contract;
import com.csm.hybrids.entity.ContractSummonEntity;
import com.csm.hybrids.hybrid.HybridType;
import dev.kosmx.playerAnim.minecraftApi.PlayerAnimationRegistry;
import net.minecraft.client.Minecraft;
import net.minecraft.client.gui.screens.TitleScreen;
import net.minecraft.client.resources.model.BakedModel;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.packs.resources.ResourceManager;
import net.minecraft.world.item.Item;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.client.event.ScreenEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;
import net.minecraftforge.registries.ForgeRegistries;
import software.bernie.geckolib.cache.GeckoLibCache;

import java.util.ArrayList;
import java.util.LinkedHashSet;
import java.util.List;
import java.util.Set;

/**
 * Logs, once the game reaches the title screen, whether the mod's assets actually loaded: how many textures, models
 * and animations there are, and every item, move icon or model that is missing. If the game's resource loading broke
 * (another mod or a resource pack failing can take everyone's assets down with it), this says so in latest.log,
 * as {@code [csm] assets ...} lines.
 */
@Mod.EventBusSubscriber(modid = CsmMod.MODID, bus = Mod.EventBusSubscriber.Bus.FORGE, value = Dist.CLIENT)
public final class AssetCheck {
    private static boolean checked;

    @SubscribeEvent
    public static void onScreen(ScreenEvent.Init.Post event) {
        if (!checked && event.getScreen() instanceof TitleScreen) {
            checked = true;
            try {
                run();
            } catch (RuntimeException | LinkageError e) {
                CsmMod.LOGGER.error("[csm] assets: the check itself failed", e);
            }
        }
    }

    /** @return how many things are missing */
    public static int run() {
        Minecraft mc = Minecraft.getInstance();
        ResourceManager rm = mc.getResourceManager();
        String ns = CsmMod.MODID;
        int textures = rm.listResources("textures", p -> p.getNamespace().equals(ns) && p.getPath().endsWith(".png")).size();
        long models = GeckoLibCache.getBakedModels().keySet().stream().filter(k -> k.getNamespace().equals(ns)).count();
        long animations = GeckoLibCache.getBakedAnimations().keySet().stream().filter(k -> k.getNamespace().equals(ns)).count();
        int playerAnims = PlayerAnimationRegistry.getModAnimations(ns).size();
        CsmMod.LOGGER.info("[csm] assets: {} textures, {} models, {} model animations, {} player animations", textures,
                models, animations, playerAnims);
        if (textures == 0 || models == 0) {
            CsmMod.LOGGER.error("[csm] assets: the mod's textures/models did not load at all. Look further up this log for "
                    + "'Caught error loading resourcepacks' or a GeckoLib error: something failed while the game loaded its "
                    + "resources and took the mod's assets with it");
        }

        List<String> missing = new ArrayList<>();
        // items that would show as the purple-and-black missing model
        BakedModel missingModel = mc.getModelManager().getMissingModel();
        for (Item item : ForgeRegistries.ITEMS.getValues()) {
            ResourceLocation id = ForgeRegistries.ITEMS.getKey(item);
            if (id != null && id.getNamespace().equals(ns)
                    && mc.getItemRenderer().getItemModelShaper().getItemModel(item) == missingModel) {
                missing.add("item model " + id);
            }
        }
        // move icons, the models and textures every form, devil and contract summon is drawn with
        Set<Ability> abilities = new LinkedHashSet<>();
        for (HybridType type : HybridType.values()) {
            abilities.addAll(type.abilities());
            if (type == HybridType.NONE) {
                continue;
            }
            // devils as mobs (and a player's monster form); hybrids, fiends and the humanoid devils' player parts
            if (type.devil) {
                model(rm, missing, "entity/devil/" + type.id);
            }
            if (!type.devil || type.humanoid) {
                model(rm, missing, "hybrid/" + type.id);
            }
        }
        for (Contract c : Contract.values()) {
            abilities.addAll(c.abilities());
        }
        for (ContractSummonEntity.Kind kind : ContractSummonEntity.Kind.values()) {
            model(rm, missing, "entity/contract/" + kind.model);
        }
        for (Ability a : abilities) {
            if (rm.getResource(a.icon()).isEmpty()) {
                missing.add("icon " + a.icon().getPath());
            }
        }
        if (!missing.isEmpty()) {
            CsmMod.LOGGER.error("[csm] assets: {} missing: {}", missing.size(), missing);
        } else {
            CsmMod.LOGGER.info("[csm] assets: everything is there");
        }
        return missing.size();
    }

    private static void model(ResourceManager rm, List<String> missing, String name) {
        need(rm, missing, "geo/" + name + ".geo.json", true);
        need(rm, missing, "animations/" + name + ".animation.json", true);
        need(rm, missing, "textures/" + name + ".png", false);
    }

    /** A file must exist, and a GeckoLib model or animation must have loaded into GeckoLib's cache too. */
    private static void need(ResourceManager rm, List<String> missing, String path, boolean gecko) {
        ResourceLocation id = CsmMod.id(path);
        if (rm.getResource(id).isEmpty()) {
            missing.add(path);
        } else if (gecko && path.startsWith("geo/") && !GeckoLibCache.getBakedModels().containsKey(id)) {
            missing.add(path + " (not loaded by GeckoLib)");
        } else if (gecko && path.startsWith("animations/") && !GeckoLibCache.getBakedAnimations().containsKey(id)) {
            missing.add(path + " (not loaded by GeckoLib)");
        }
    }

    private AssetCheck() {
    }
}
