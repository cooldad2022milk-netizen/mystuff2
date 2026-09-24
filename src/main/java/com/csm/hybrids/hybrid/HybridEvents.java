package com.csm.hybrids.hybrid;

import com.csm.hybrids.CsmMod;
import com.csm.hybrids.ability.AbilityUtil;
import com.csm.hybrids.ability.bomb.BombAbilities;
import com.csm.hybrids.ability.katana.KatanaAbilities;
import com.csm.hybrids.ability.longsword.LongswordAbilities;
import com.csm.hybrids.ability.shark.SharkAbilities;
import com.csm.hybrids.command.CsmCommand;
import com.csm.hybrids.fx.Blast;
import com.csm.hybrids.fx.Fx;
import com.csm.hybrids.registry.ModItems;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.tags.DamageTypeTags;
import net.minecraft.world.InteractionResult;
import net.minecraft.world.damagesource.DamageSource;
import net.minecraft.world.damagesource.DamageTypes;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.Items;
import net.minecraftforge.event.AttachCapabilitiesEvent;
import net.minecraftforge.event.RegisterCommandsEvent;
import net.minecraftforge.event.TickEvent;
import net.minecraftforge.event.entity.living.LivingAttackEvent;
import net.minecraftforge.event.entity.living.LivingDeathEvent;
import net.minecraftforge.event.entity.living.LivingHurtEvent;
import net.minecraftforge.event.entity.player.PlayerEvent;
import net.minecraftforge.event.entity.player.PlayerInteractEvent;
import net.minecraftforge.eventbus.api.EventPriority;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;

@Mod.EventBusSubscriber(modid = CsmMod.MODID)
public final class HybridEvents {

    @SubscribeEvent
    public static void attach(AttachCapabilitiesEvent<Entity> event) {
        if (event.getObject() instanceof Player) {
            HybridCapability.Provider provider = new HybridCapability.Provider();
            event.addCapability(HybridCapability.KEY, provider);
            event.addListener(provider::invalidate);
        }
    }

    @SubscribeEvent
    public static void clone(PlayerEvent.Clone event) {
        event.getOriginal().reviveCaps();
        HybridData old = HybridCapability.get(event.getOriginal());
        HybridData now = HybridCapability.get(event.getEntity());
        if (old != null && now != null) {
            now.copyFrom(old, event.isWasDeath());
        }
        event.getOriginal().invalidateCaps();
    }

    @SubscribeEvent
    public static void login(PlayerEvent.PlayerLoggedInEvent event) {
        refresh(event.getEntity());
    }

    @SubscribeEvent
    public static void respawn(PlayerEvent.PlayerRespawnEvent event) {
        refresh(event.getEntity());
    }

    @SubscribeEvent
    public static void changeDim(PlayerEvent.PlayerChangedDimensionEvent event) {
        refresh(event.getEntity());
    }

    private static void refresh(Player player) {
        if (player instanceof ServerPlayer sp) {
            HybridData data = HybridCapability.get(sp);
            if (data != null) {
                data.activeRun = null;
                if (data.isTransformed()) {
                    HybridLogic.applyAttributes(sp, data);
                } else {
                    HybridLogic.removeAttributes(sp);
                }
                com.csm.hybrids.contract.Contracts.applyToll(sp, data);
                sp.refreshDimensions();
                HybridLogic.sync(sp, data);
            }
        }
    }

    /** A player in a monster devil's form takes up the devil's room (and sees from its eyes). */
    @SubscribeEvent
    @SuppressWarnings("removal") // EntityEvent.Size is still how 47.x resizes entities
    public static void size(net.minecraftforge.event.entity.EntityEvent.Size event) {
        if (!(event.getEntity() instanceof Player player)) {
            return;
        }
        HybridData data = HybridCapability.get(player);
        if (data == null || !data.isTransformed() || !data.type().monster()) {
            return;
        }
        com.csm.hybrids.devil.DevilSpec spec = com.csm.hybrids.devil.DevilSpecs.of(data.type());
        event.setNewSize(net.minecraft.world.entity.EntityDimensions.scalable(spec.playerWidth, spec.playerHeight), false);
        event.setNewEyeHeight(spec.playerEye);
    }

    /** Thralls (mobs a devil controls) never turn on their master or on each other. */
    @SubscribeEvent
    public static void thrallTarget(net.minecraftforge.event.entity.living.LivingChangeTargetEvent event) {
        LivingEntity mob = event.getEntity();
        LivingEntity target = event.getNewTarget();
        if (target == null || !mob.getPersistentData().hasUUID(com.csm.hybrids.entity.devil.DevilEntity.THRALL_TAG)) {
            return;
        }
        java.util.UUID master = mob.getPersistentData().getUUID(com.csm.hybrids.entity.devil.DevilEntity.THRALL_TAG);
        if (target.getUUID().equals(master) || (target.getPersistentData().hasUUID(com.csm.hybrids.entity.devil.DevilEntity.THRALL_TAG)
                && target.getPersistentData().getUUID(com.csm.hybrids.entity.devil.DevilEntity.THRALL_TAG).equals(master))) {
            event.setCanceled(true);
        }
    }

    @SubscribeEvent
    public static void logout(PlayerEvent.PlayerLoggedOutEvent event) {
        HybridData data = HybridCapability.get(event.getEntity());
        if (data != null) {
            data.activeRun = null;
        }
    }

    @SubscribeEvent
    public static void startTracking(PlayerEvent.StartTracking event) {
        if (event.getTarget() instanceof ServerPlayer target && event.getEntity() instanceof ServerPlayer viewer) {
            HybridLogic.syncTo(target, viewer);
        }
    }

    @SubscribeEvent
    public static void tick(TickEvent.PlayerTickEvent event) {
        if (event.phase == TickEvent.Phase.END && event.player instanceof ServerPlayer sp) {
            HybridLogic.tick(sp);
        } else if (event.phase == TickEvent.Phase.END && event.player.level().isClientSide) {
            HybridData data = HybridCapability.get(event.player);
            if (data != null) {
                data.tickCooldowns();
            }
        }
    }

    @SubscribeEvent(priority = EventPriority.HIGH)
    public static void death(LivingDeathEvent event) {
        if (event.getEntity() instanceof ServerPlayer sp && !event.getSource().is(DamageTypeTags.BYPASSES_INVULNERABILITY)) {
            HybridData data = HybridCapability.get(sp);
            if (data != null && HybridLogic.tryRevive(sp, data)) {
                event.setCanceled(true);
            }
        }
    }

    @SubscribeEvent
    public static void attacked(LivingAttackEvent event) {
        if (event.getEntity() instanceof ServerPlayer sp && event.getSource().is(DamageTypeTags.IS_FIRE)) {
            HybridData data = HybridCapability.get(sp);
            if (data != null && data.isTransformed() && data.type() == HybridType.FLAMETHROWER) {
                event.setCanceled(true);
                sp.clearFire();
            }
        }
    }

    /**
     * Beam can't be touched while he is under the ground; Katana Man's iai stance cuts down the first attacker.
     */
    @SubscribeEvent
    public static void untouchable(LivingAttackEvent event) {
        if (!(event.getEntity() instanceof ServerPlayer sp) || event.getSource().is(DamageTypeTags.BYPASSES_INVULNERABILITY)) {
            return;
        }
        if (SharkAbilities.submerged(sp) && !event.getSource().is(net.minecraft.tags.DamageTypeTags.IS_DROWNING)) {
            event.setCanceled(true);
            return;
        }
        HybridData data = HybridCapability.get(sp);
        if (data != null && data.activeRun != null && data.activeRun.ability instanceof KatanaAbilities.IaiCounter
                && data.activeRun.counter == 0 && event.getSource().getEntity() != null) {
            KatanaAbilities.IaiCounter.counter(sp, data.activeRun, event.getSource().getEntity());
            event.setCanceled(true);
        }
    }

    /** Sword Man's cross-guard takes most of a blow and throws it back. */
    @SubscribeEvent(priority = EventPriority.HIGH)
    public static void guarded(LivingHurtEvent event) {
        if (!(event.getEntity() instanceof ServerPlayer sp)) {
            return;
        }
        HybridData data = HybridCapability.get(sp);
        if (data != null && data.activeRun != null && data.activeRun.ability instanceof LongswordAbilities.CrossGuard
                && !event.getSource().is(DamageTypeTags.BYPASSES_INVULNERABILITY)) {
            event.setAmount(LongswordAbilities.CrossGuard.block(sp, event.getAmount(), event.getSource().getEntity()));
        }
    }

    /** Hurting things while in devil form spills their blood into you. */
    @SubscribeEvent
    public static void hurt(LivingHurtEvent event) {
        DamageSource src = event.getSource();
        if (!(src.getEntity() instanceof ServerPlayer sp) || event.getEntity() == sp) {
            return;
        }
        HybridData data = HybridCapability.get(sp);
        if (data == null || !data.isHybrid() || (!data.isTransformed() && !data.type().fiend)) {
            return;
        }
        LivingEntity target = event.getEntity();
        HybridLogic.addBlood(sp, Math.min(event.getAmount(), 30f) * 0.35f);
        boolean melee = src.getDirectEntity() == sp && src.is(DamageTypes.PLAYER_ATTACK) && sp.getMainHandItem().isEmpty();
        if (melee) {
            ServerLevel level = sp.serverLevel();
            switch (data.type()) {
                case CHAINSAW, CHAINSAW_DEVIL -> {
                    AbilityUtil.blood(level, target.getBoundingBox().getCenter(), 22, 0.25);
                    level.playSound(null, target.getX(), target.getY(), target.getZ(),
                            com.csm.hybrids.registry.ModSounds.CHAINSAW_CUT.get(), SoundSource.PLAYERS, 0.8f, 1.1f);
                }
                case FLAMETHROWER -> target.setSecondsOnFire(4);
                case CROSSBOW -> AbilityUtil.blood(level, target.getBoundingBox().getCenter(), 8, 0.2);
                case WHIP -> {
                    AbilityUtil.blood(level, target.getBoundingBox().getCenter(), 14, 0.25);
                    Fx.bloodSpray(level, target.getBoundingBox().getCenter(), sp.getLookAngle(), 8, 0.35);
                }
                case KATANA, LONGSWORD -> {
                    AbilityUtil.blood(level, target.getBoundingBox().getCenter(), 18, 0.25);
                    Fx.slash(level, target.getBoundingBox().getCenter(), sp.getLookAngle().add(0, 0.5, 0), 1.2);
                }
                case BLOOD -> {
                    AbilityUtil.blood(level, target.getBoundingBox().getCenter(), 20, 0.25);
                    HybridLogic.addBlood(sp, 2f);
                }
                case SHARK -> AbilityUtil.blood(level, target.getBoundingBox().getCenter(), 22, 0.25);
                case VIOLENCE -> {
                    AbilityUtil.push(target, sp.position(), 0.9, 0.25);
                    Fx.impact(level, target.getBoundingBox().getCenter(), 0.9);
                }
                case SPEAR -> {
                    AbilityUtil.blood(level, target.getBoundingBox().getCenter(), 16, 0.2);
                    Fx.bloodSpray(level, target.getBoundingBox().getCenter(), sp.getLookAngle(), 10, 0.45);
                }
                case BOMB -> {
                    // every punch detonates (never while soaked)
                    if (!BombAbilities.tooWet(sp)) {
                        Blast.detonate(level, sp, null, target.getBoundingBox().getCenter(), 1.3f, 3f, false);
                    }
                }
                default -> {
                }
            }
        }
    }

    /** Glass bottle on a living creature -> Blood Vial. */
    @SubscribeEvent
    public static void bottleBlood(PlayerInteractEvent.EntityInteract event) {
        ItemStack held = event.getItemStack();
        if (!held.is(Items.GLASS_BOTTLE) || !(event.getTarget() instanceof LivingEntity target) || target instanceof Player) {
            return;
        }
        if (event.getLevel().isClientSide) {
            event.setCancellationResult(InteractionResult.SUCCESS);
            event.setCanceled(true);
            return;
        }
        Player player = event.getEntity();
        target.hurt(player.damageSources().playerAttack(player), 2f);
        if (!player.getAbilities().instabuild) {
            held.shrink(1);
        }
        ItemStack vial = new ItemStack(ModItems.BLOOD_VIAL.get());
        if (!player.getInventory().add(vial)) {
            player.drop(vial, false);
        }
        if (player.level() instanceof ServerLevel sl) {
            AbilityUtil.blood(sl, target.getBoundingBox().getCenter(), 10, 0.15);
        }
        player.level().playSound(null, target.getX(), target.getY(), target.getZ(), SoundEvents.BOTTLE_FILL, SoundSource.PLAYERS, 1f, 0.8f);
        event.setCancellationResult(InteractionResult.SUCCESS);
        event.setCanceled(true);
    }

    @SubscribeEvent
    public static void commands(RegisterCommandsEvent event) {
        CsmCommand.register(event.getDispatcher());
    }

    private HybridEvents() {
    }
}
