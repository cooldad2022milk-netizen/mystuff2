package com.csm.hybrids.contract;

import com.csm.hybrids.ability.AbilityUtil;
import com.csm.hybrids.ability.devil.ControlMoves;
import com.csm.hybrids.entity.ContractSummonEntity;
import com.csm.hybrids.entity.devil.DevilEntity;
import com.csm.hybrids.fx.Fx;
import com.csm.hybrids.hybrid.HybridData;
import com.csm.hybrids.hybrid.HybridLogic;
import com.csm.hybrids.registry.ModSounds;
import net.minecraft.ChatFormatting;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.nbt.ListTag;
import net.minecraft.nbt.Tag;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.effect.MobEffectInstance;
import net.minecraft.world.effect.MobEffects;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.Mob;
import net.minecraft.world.entity.ai.attributes.AttributeInstance;
import net.minecraft.world.entity.ai.attributes.AttributeModifier;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.phys.BlockHitResult;
import net.minecraft.world.phys.HitResult;
import net.minecraft.world.phys.Vec3;
import org.jetbrains.annotations.Nullable;

import java.util.UUID;

/** Making contracts, and the prices that are paid later (the Curse Devil's toll on your lifespan). */
public final class Contracts {
    private static final UUID TOLL_ID = UUID.fromString("7c1d8f0e-3b8a-4a8e-9f2e-5a1b2c3d4e09");
    /** The Curse stops taking lifespan once this many hearts are gone (it still comes when called). */
    public static final int MAX_TOLL = 7;

    /**
     * Sign {@code c}: the devil takes its price and the contract is yours.
     *
     * @return false if the player already holds it
     */
    public static boolean sign(ServerPlayer player, HybridData data, Contract c) {
        if (!data.addContract(c)) {
            return false;
        }
        ServerLevel level = player.serverLevel();
        Vec3 chest = player.position().add(0, 1.2, 0);
        switch (c) {
            case FOX_HEAD, FOX_PAW -> {
                // the fox takes its first mouthful of you
                if (!player.getAbilities().instabuild) {
                    player.setHealth(Math.max(1f, player.getHealth() - 4f));
                }
                AbilityUtil.blood(level, chest, 30, 0.3);
                AbilityUtil.sound(player, ModSounds.DEVIL_BITE.get(), 1.0f, 1.3f);
            }
            case CURSE -> AbilityUtil.sound(player, ModSounds.DEVIL_ROAR.get(), 0.7f, 0.5f);
            case FUTURE -> {
                player.addEffect(AbilityUtil.quiet(new MobEffectInstance(MobEffects.DARKNESS, 60, 0, false, false)));
                AbilityUtil.sound(player, ModSounds.COSMOS_HALLOWEEN.get(), 0.9f, 1.5f);
                Fx.stars(level, player.getEyePosition(), 12, 0.3);
            }
            case GHOST -> {
                // it takes your right eye
                player.addEffect(AbilityUtil.quiet(new MobEffectInstance(MobEffects.BLINDNESS, 80, 0, false, false)));
                AbilityUtil.blood(level, player.getEyePosition(), 16, 0.1);
                AbilityUtil.sound(player, ModSounds.HEART_RIP.get(), 0.9f, 1.4f);
            }
            case SNAKE -> {
                // the first fingernail
                if (!player.getAbilities().instabuild) {
                    player.setHealth(Math.max(1f, player.getHealth() - 1f));
                }
                AbilityUtil.blood(level, AbilityUtil.handPos(player, true, 0.2), 8, 0.08);
                AbilityUtil.sound(player, ModSounds.HEART_RIP.get(), 0.6f, 1.8f);
            }
            case OCTOPUS -> {
                Fx.ink(level, player.position().add(0, 1.0, 0), 30, 1.2);
                player.causeFoodExhaustion(12f);
                AbilityUtil.sound(player, ModSounds.SHARK_DIVE.get(), 0.9f, 0.6f);
            }
            case HELL -> {
                Fx.fireBurst(level, player.position().add(0, 0.2, 0), 30, 0.3);
                player.addEffect(AbilityUtil.quiet(new MobEffectInstance(MobEffects.DARKNESS, 80, 0, false, false)));
                AbilityUtil.sound(player, ModSounds.DEVIL_ROAR.get(), 0.6f, 0.4f);
            }
            case DOLL -> {
                // something in you goes stiff for a moment
                player.addEffect(AbilityUtil.quiet(new MobEffectInstance(MobEffects.MOVEMENT_SLOWDOWN, 60, 3, false, false)));
                AbilityUtil.sound(player, ModSounds.CONTROL_DOMINATE.get(), 0.7f, 1.6f);
            }
        }
        player.displayClientMessage(Component.translatable("msg.csm.contract_signed." + c.id)
                .withStyle(ChatFormatting.DARK_RED), false);
        HybridLogic.sync(player, data);
        return true;
    }

    /** Break a contract (commands only: devils don't let go that easily). */
    public static boolean breakContract(ServerPlayer player, HybridData data, Contract c) {
        if (!data.removeContract(c)) {
            return false;
        }
        if (data.activeRun != null && data.activeRun.ability instanceof ContractAbility ca && ca.contract == c) {
            HybridLogic.cancelRun(player, data);
        }
        HybridLogic.sync(player, data);
        return true;
    }

    // ------------------------------------------------------------------ the Curse Devil
    /** The third nail: the Curse Devil manifests behind the victim, and takes a heart of the contractor's lifespan. */
    public static void curseManifest(ServerPlayer player, HybridData data, LivingEntity victim) {
        ServerLevel level = player.serverLevel();
        Vec3 dir = victim.position().subtract(player.position());
        dir = new Vec3(dir.x, 0, dir.z);
        dir = dir.lengthSqr() > 1e-4 ? dir.normalize() : new Vec3(player.getLookAngle().x, 0, player.getLookAngle().z).normalize();
        Vec3 behind = victim.position().add(dir.scale(victim.getBbWidth() * 0.5 + 1.3));
        ContractSummonEntity.summon(level, ContractSummonEntity.Kind.CURSE, player, victim, behind, dir.reverse());
        AbilityUtil.sound(player, ModSounds.DEVIL_ROAR.get(), 1.6f, 0.45f);
        if (!player.getAbilities().instabuild && data.curseToll() < MAX_TOLL) {
            data.setCurseToll(data.curseToll() + 1);
            applyToll(player, data);
            player.displayClientMessage(Component.translatable("msg.csm.curse_toll", data.curseToll())
                    .withStyle(ChatFormatting.DARK_RED), true);
        }
    }

    /** Hearts of lifespan the Curse took are gone for good: max health is lowered by that much. */
    public static void applyToll(ServerPlayer player, HybridData data) {
        AttributeInstance hp = player.getAttribute(Attributes.MAX_HEALTH);
        if (hp == null) {
            return;
        }
        hp.removeModifier(TOLL_ID);
        int toll = Math.min(data.curseToll(), MAX_TOLL);
        if (toll > 0) {
            hp.addTransientModifier(new AttributeModifier(TOLL_ID, "csm_curse_toll", -2.0 * toll,
                    AttributeModifier.Operation.ADDITION));
        }
        if (player.getHealth() > player.getMaxHealth()) {
            player.setHealth(player.getMaxHealth());
        }
    }

    // ------------------------------------------------------------------ the Snake Devil
    /** Where the Snake Devil keeps what it has swallowed: with its contractor (entity data, last in first out). */
    public static final String BELLY = "csm_snake_belly";
    public static final int BELLY_SIZE = 3;

    /** How many creatures the snake is holding for {@code player}. */
    public static int bellyCount(ServerPlayer player) {
        return player.getPersistentData().getList(BELLY, Tag.TAG_COMPOUND).size();
    }

    /** Whether the Snake Devil can swallow {@code e} whole (anything but people and the great devils). */
    public static boolean swallowable(LivingEntity e) {
        return e instanceof Mob && e.isAlive() && e.getMaxHealth() <= 120f && e.getBbWidth() < 3f
                && !e.getType().is(net.minecraftforge.common.Tags.EntityTypes.BOSSES)
                && !(e instanceof DevilEntity d && d.spec().boss);
    }

    /**
     * The snake swallows {@code e} whole: it is gone from the world and kept in the belly until {@link #release}.
     *
     * @return false if the belly is full or it can't be kept (it only gets bitten then)
     */
    public static boolean swallow(ServerPlayer owner, LivingEntity e) {
        ListTag belly = owner.getPersistentData().getList(BELLY, Tag.TAG_COMPOUND);
        if (belly.size() >= BELLY_SIZE || !swallowable(e)) {
            return false;
        }
        e.stopRiding();
        e.ejectPassengers();
        CompoundTag tag = new CompoundTag();
        if (!e.save(tag)) {
            return false;
        }
        tag.remove("UUID");
        tag.remove("Passengers");
        belly.add(tag);
        owner.getPersistentData().put(BELLY, belly);
        e.discard();
        return true;
    }

    /**
     * The snake spits the last thing it swallowed back out at {@code at}: whole again, and fighting for its contractor
     * for two minutes (Sawatari's snake let the Ghost Devil out to fight Aki).
     */
    @Nullable
    public static LivingEntity release(ServerPlayer owner, Vec3 at, float yaw) {
        ListTag belly = owner.getPersistentData().getList(BELLY, Tag.TAG_COMPOUND);
        if (belly.isEmpty()) {
            return null;
        }
        CompoundTag tag = belly.getCompound(belly.size() - 1);
        belly.remove(belly.size() - 1);
        owner.getPersistentData().put(BELLY, belly);
        ServerLevel level = owner.serverLevel();
        Entity made = EntityType.create(tag, level).orElse(null);
        if (!(made instanceof LivingEntity le)) {
            return null;
        }
        le.moveTo(at.x, at.y, at.z, yaw, 0f);
        le.setYHeadRot(yaw);
        le.setHealth(le.getMaxHealth());
        le.removeAllEffects();
        le.clearFire();
        le.fallDistance = 0;
        le.setDeltaMovement(0, 0.3, 0);
        CompoundTag data = le.getPersistentData();
        data.remove(DOLL);
        if (le instanceof Mob m) {
            DevilEntity.enthrall(m, owner.getUUID());
            data.putLong(ControlMoves.THRALL_UNTIL, level.getGameTime() + 2400);
            m.setTarget(null);
        }
        level.addFreshEntity(le);
        return le;
    }

    // ------------------------------------------------------------------ the Doll Devil
    /** Set on a creature the Doll Devil has made into a doll (it is also a thrall of the contractor). */
    public static final String DOLL = "csm_doll";
    /** A contractor can only keep this many dolls at once. */
    public static final int MAX_DOLLS = 12;
    /** Past this distance from the contractor a doll falls over, lifeless. */
    public static final double DOLL_RANGE = 48;

    /** Whether the Doll Devil's touch works on {@code e}: people and beasts, never devils, hybrids or fiends. */
    public static boolean dollable(LivingEntity e) {
        return e instanceof Mob && e.isAlive() && !(e instanceof DevilEntity)
                && !e.getType().is(net.minecraftforge.common.Tags.EntityTypes.BOSSES)
                && e.getAttribute(Attributes.ATTACK_DAMAGE) != null && !e.getPersistentData().getBoolean(DOLL);
    }

    /** How many dolls {@code master} has within reach. */
    public static int dollCount(ServerLevel level, LivingEntity master) {
        return level.getEntitiesOfClass(Mob.class, master.getBoundingBox().inflate(DOLL_RANGE),
                m -> m.getPersistentData().getBoolean(DOLL) && m.getPersistentData().hasUUID(DevilEntity.THRALL_TAG)
                        && m.getPersistentData().getUUID(DevilEntity.THRALL_TAG).equals(master.getUUID())).size();
    }

    /**
     * {@code e} becomes {@code master}'s doll: it obeys them, one of its arms is a blade now, and it can't be turned
     * back.
     *
     * @return false if the touch does nothing to it (or the contractor has all the dolls they can keep)
     */
    public static boolean makeDoll(ServerLevel level, LivingEntity master, LivingEntity e) {
        if (!dollable(e) || dollCount(level, master) >= MAX_DOLLS) {
            return false;
        }
        Mob m = (Mob) e;
        CompoundTag data = m.getPersistentData();
        data.putBoolean(DOLL, true);
        DevilEntity.enthrall(m, master.getUUID());
        data.putLong(ControlMoves.THRALL_UNTIL, Long.MAX_VALUE / 2);
        m.setTarget(null);
        m.setPersistenceRequired();
        m.addEffect(AbilityUtil.quiet(new MobEffectInstance(MobEffects.DAMAGE_BOOST, 600, 1)));
        Vec3 c = m.getBoundingBox().getCenter();
        Fx.stars(level, m.getEyePosition().add(0, 0.3, 0), 8, 0.25);
        Fx.shockwave(level, m.position().add(0, 0.05, 0), 1.2, Fx.STEEL_RING);
        AbilityUtil.soundAt(level, c, ModSounds.CONTROL_DOMINATE.get(), 0.8f, 1.7f);
        return true;
    }

    /** A doll whose contractor is gone (dead, far away, elsewhere) falls over, lifeless. */
    public static void dropDoll(ServerLevel level, Mob doll) {
        Vec3 c = doll.getBoundingBox().getCenter();
        Fx.smoke(level, c, 8, 0.4);
        doll.getPersistentData().remove(DOLL);
        doll.invulnerableTime = 0;
        doll.hurt(doll.damageSources().magic(), Float.MAX_VALUE);
        if (doll.isAlive()) {
            doll.kill();
        }
    }

    // ------------------------------------------------------------------ the Hell Devil
    /** Lives the Hell Devil takes for sending things to Hell. */
    public static final int HELL_PRICE = 3;

    /**
     * The three lives the Hell Devil would take right now: the contractor's dolls nearest first, then other creatures
     * nearby that aren't hostile (never a player, never a great devil). Fewer than {@link #HELL_PRICE}: it won't come.
     */
    public static java.util.List<LivingEntity> hellOfferings(ServerPlayer player) {
        ServerLevel level = player.serverLevel();
        java.util.List<LivingEntity> near = level.getEntitiesOfClass(LivingEntity.class,
                player.getBoundingBox().inflate(16), e -> e != player && e.isAlive() && !(e instanceof net.minecraft.world.entity.player.Player)
                        && !(e instanceof DevilEntity d && d.spec().boss)
                        && !e.getType().is(net.minecraftforge.common.Tags.EntityTypes.BOSSES)
                        && (isDollOf(e, player) || !(e instanceof net.minecraft.world.entity.monster.Enemy)));
        near.sort(java.util.Comparator.<LivingEntity>comparingInt(e -> isDollOf(e, player) ? 0 : 1)
                .thenComparingDouble(e -> e.distanceToSqr(player)));
        return near.subList(0, Math.min(HELL_PRICE, near.size()));
    }

    private static boolean isDollOf(LivingEntity e, LivingEntity master) {
        CompoundTag t = e.getPersistentData();
        return t.getBoolean(DOLL) && t.hasUUID(DevilEntity.THRALL_TAG) && t.getUUID(DevilEntity.THRALL_TAG).equals(master.getUUID());
    }

    // ------------------------------------------------------------------ aiming
    /** Where a summon lands when nothing is under the crosshair: the block looked at, or the ground ahead. */
    public static Vec3 aimPoint(ServerPlayer player, double range) {
        BlockHitResult block = AbilityUtil.raycastBlock(player, range);
        Vec3 p = block.getType() == HitResult.Type.MISS
                ? player.getEyePosition().add(player.getLookAngle().scale(Math.min(range, 8)))
                : block.getLocation();
        Vec3 ground = AbilityUtil.groundBelow(player.serverLevel(), p, 12);
        return ground != null ? ground : p;
    }

    private Contracts() {
    }
}
