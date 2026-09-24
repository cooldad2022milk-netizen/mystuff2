package com.csm.hybrids.devil;

import com.csm.hybrids.CsmMod;
import com.csm.hybrids.ability.AbilityUtil;
import com.csm.hybrids.ability.devil.ContractMoves;
import com.csm.hybrids.ability.devil.ControlMoves;
import com.csm.hybrids.entity.devil.DevilEntity;
import com.csm.hybrids.fx.Fx;
import com.csm.hybrids.hybrid.HybridCapability;
import com.csm.hybrids.hybrid.HybridData;
import com.csm.hybrids.hybrid.HybridType;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.tags.DamageTypeTags;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.Mob;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.phys.AABB;
import net.minecraft.world.phys.Vec3;
import net.minecraftforge.event.entity.living.LivingAttackEvent;
import net.minecraftforge.event.entity.living.LivingEvent;
import net.minecraftforge.eventbus.api.EventPriority;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;

import java.util.List;
import java.util.UUID;

/** Standing rules of the full devils that are not tied to one move. */
@Mod.EventBusSubscriber(modid = CsmMod.MODID)
public final class DevilEvents {

    /**
     * The Prime Minister's contract: harm meant for Makima lands on some random creature nearby instead. It is always
     * in force against a blow that would kill the Control Devil herself, and for 20 seconds against every blow once
     * the contract move is used. Chainsaw Man is the exception - he does not attack her, he eats her.
     */
    @SubscribeEvent(priority = EventPriority.HIGH)
    public static void contract(LivingAttackEvent event) {
        LivingEntity victim = event.getEntity();
        if (!(victim.level() instanceof ServerLevel level) || event.getSource().is(DamageTypeTags.BYPASSES_INVULNERABILITY)) {
            return;
        }
        boolean active = victim.getPersistentData().getLong(ControlMoves.CONTRACT_UNTIL) > level.getGameTime();
        boolean lethalToMakima = victim instanceof DevilEntity d && d.devilType() == HybridType.CONTROL
                && event.getAmount() >= victim.getHealth();
        if (!active && !lethalToMakima) {
            return;
        }
        Entity attacker = event.getSource().getEntity();
        if (attacker instanceof ServerPlayer sp) {
            HybridData d = HybridCapability.get(sp);
            if (d != null && (d.type() == HybridType.CHAINSAW || d.type() == HybridType.CHAINSAW_DEVIL)
                    && d.isTransformed()) {
                return;
            }
        }
        List<LivingEntity> scapegoats = level.getEntitiesOfClass(LivingEntity.class,
                new AABB(victim.position(), victim.position()).inflate(24), e -> e != victim && e.isAlive()
                        && !(e instanceof Player) && e != attacker
                        && !(e instanceof DevilEntity d && d.devilType() == HybridType.CONTROL));
        if (scapegoats.isEmpty()) {
            return;
        }
        LivingEntity goat = scapegoats.get(level.random.nextInt(scapegoats.size()));
        event.setCanceled(true);
        goat.invulnerableTime = 0;
        goat.hurt(victim.damageSources().magic(), event.getAmount());
        Vec3 c = goat.getBoundingBox().getCenter();
        AbilityUtil.blood(level, c, 40, 0.35);
        Fx.impact(level, c, 1.6);
        Fx.stars(level, victim.getEyePosition(), 4, 0.3);
    }

    /** Thralls serve their master for a while: they turn on whatever the master is fighting, then come to their senses. */
    @SubscribeEvent
    public static void thralls(LivingEvent.LivingTickEvent event) {
        LivingEntity e = event.getEntity();
        if (e.tickCount % 10 != 0 || !(e instanceof Mob mob) || !(e.level() instanceof ServerLevel level)) {
            return;
        }
        CompoundTag tag = e.getPersistentData();
        if (!tag.hasUUID(DevilEntity.THRALL_TAG)) {
            return;
        }
        UUID masterId = tag.getUUID(DevilEntity.THRALL_TAG);
        Entity master = level.getEntity(masterId);
        boolean doll = tag.getBoolean(com.csm.hybrids.contract.Contracts.DOLL);
        if (doll && (!(master instanceof LivingEntity dm) || !dm.isAlive()
                || dm.distanceToSqr(e) > com.csm.hybrids.contract.Contracts.DOLL_RANGE
                * com.csm.hybrids.contract.Contracts.DOLL_RANGE)) {
            // Santa Claus has to stay near her dolls: left behind, a doll falls over, lifeless
            com.csm.hybrids.contract.Contracts.dropDoll(level, mob);
            return;
        }
        if (doll && e.tickCount % 200 == 0) {
            // one arm is a blade now
            mob.addEffect(AbilityUtil.quiet(new net.minecraft.world.effect.MobEffectInstance(
                    net.minecraft.world.effect.MobEffects.DAMAGE_BOOST, 600, 1)));
        }
        if (level.getGameTime() > tag.getLong(ControlMoves.THRALL_UNTIL) || !(master instanceof LivingEntity m)
                || !m.isAlive()) {
            tag.remove(DevilEntity.THRALL_TAG);
            tag.remove(ControlMoves.THRALL_UNTIL);
            if (mob.getTarget() != null && mob.getTarget().getUUID().equals(masterId)) {
                mob.setTarget(null);
            }
            return;
        }
        LivingEntity wanted = null;
        if (m instanceof Mob mm) {
            wanted = mm.getTarget();
        } else if (m instanceof Player p && p.tickCount - p.getLastHurtMobTimestamp() < 200) {
            wanted = p.getLastHurtMob();
        }
        if (wanted != null && wanted.isAlive() && wanted != mob && !isThrallOf(wanted, masterId)) {
            mob.setTarget(wanted);
        } else if (mob.getTarget() != null && (mob.getTarget() == m || isThrallOf(mob.getTarget(), masterId))) {
            mob.setTarget(null);
        }
        if (e.tickCount % 40 == 0) {
            Vec3 h = e.getEyePosition().add(0, 0.55, 0);
            level.sendParticles(com.csm.hybrids.registry.ModParticles.STAR.get(), h.x, h.y, h.z, 1, 0.15, 0.05, 0.15, 0.0);
        }
    }

    // ------------------------------------------------------------------ deaths: the Zombie Devil's bite, tomato seeds
    private record Rebirth(ServerLevel level, Vec3 pos, long at) {
    }

    private static final List<Rebirth> REBIRTHS = new java.util.ArrayList<>();
    public static final String REBORN = "csm_reborn";

    @SubscribeEvent
    public static void deaths(net.minecraftforge.event.entity.living.LivingDeathEvent event) {
        LivingEntity dead = event.getEntity();
        if (!(dead.level() instanceof ServerLevel level)) {
            return;
        }
        CompoundTag tag = dead.getPersistentData();
        // bitten by the Zombie Devil: it gets back up as one of its zombies
        if (tag.hasUUID(com.csm.hybrids.ability.devil.EarlyDevilMoves.BITTEN_BY)
                && tag.getLong(com.csm.hybrids.ability.devil.EarlyDevilMoves.BITTEN_UNTIL) > level.getGameTime()
                && !(dead instanceof DevilEntity)) {
            Entity master = level.getEntity(tag.getUUID(com.csm.hybrids.ability.devil.EarlyDevilMoves.BITTEN_BY));
            if (master instanceof LivingEntity m && m.isAlive()) {
                com.csm.hybrids.ability.devil.EarlyDevilMoves.raiseZombie(level, dead.position(), m);
            }
        }
        // the Tomato Devil comes back from its seeds (unless it was burned)
        if (dead instanceof DevilEntity d && d.devilType() == HybridType.TOMATO && !tag.getBoolean(REBORN)
                && !event.getSource().is(DamageTypeTags.IS_FIRE)
                && !event.getSource().is(DamageTypeTags.BYPASSES_INVULNERABILITY)) {
            REBIRTHS.add(new Rebirth(level, dead.position(), level.getGameTime() + 200));
            level.sendParticles(com.csm.hybrids.registry.ModParticles.CLOD.get(), dead.getX(), dead.getY() + 0.5,
                    dead.getZ(), 24, 1.0, 0.3, 1.0, 0.2);
        }
    }

    @SubscribeEvent
    public static void rebirths(net.minecraftforge.event.TickEvent.ServerTickEvent event) {
        if (event.phase != net.minecraftforge.event.TickEvent.Phase.END || REBIRTHS.isEmpty()) {
            return;
        }
        REBIRTHS.removeIf(r -> {
            if (r.level.getGameTime() < r.at) {
                return false;
            }
            DevilEntity t = com.csm.hybrids.registry.ModEntities.devil(HybridType.TOMATO).create(r.level);
            if (t != null) {
                t.moveTo(r.pos.x, r.pos.y, r.pos.z, r.level.random.nextFloat() * 360f, 0);
                t.getPersistentData().putBoolean(REBORN, true);
                t.setHealth(t.getMaxHealth() * 0.6f);
                r.level.addFreshEntity(t);
                t.triggerAnim("action", "manifest");
                AbilityUtil.blood(r.level, r.pos.add(0, 1, 0), 40, 0.8);
                Fx.clods(r.level, r.pos, 20, 0.4);
            }
            return true;
        });
    }

    // ------------------------------------------------------------------ the Eternity Devil's infinite floor
    private record Loop(ServerLevel level, UUID owner, Vec3 anchor, double radius, long until, java.util.Set<UUID> trapped) {
    }

    private static final List<Loop> LOOPS = new java.util.ArrayList<>();

    public static void loopZone(ServerLevel level, LivingEntity owner, Vec3 anchor, double radius, int ticks,
                                List<LivingEntity> caught) {
        java.util.Set<UUID> ids = new java.util.HashSet<>();
        caught.forEach(e -> ids.add(e.getUUID()));
        LOOPS.add(new Loop(level, owner.getUUID(), anchor, radius, level.getGameTime() + ticks, ids));
    }

    /** Whoever walks out of the loop walks back in on the far side. */
    @SubscribeEvent
    public static void loops(net.minecraftforge.event.TickEvent.ServerTickEvent event) {
        if (event.phase != net.minecraftforge.event.TickEvent.Phase.END || LOOPS.isEmpty()) {
            return;
        }
        LOOPS.removeIf(z -> {
            long now = z.level.getGameTime();
            if (now > z.until) {
                return true;
            }
            if (now % 20 == 0) {
                Fx.shockwave(z.level, z.anchor, z.radius, Fx.BLOOD_RING);
            }
            for (UUID id : z.trapped) {
                Entity e = z.level.getEntity(id);
                if (!(e instanceof LivingEntity l) || !l.isAlive()) {
                    continue;
                }
                Vec3 off = new Vec3(l.getX() - z.anchor.x, 0, l.getZ() - z.anchor.z);
                if (off.lengthSqr() > z.radius * z.radius) {
                    Vec3 to = z.anchor.subtract(off.normalize().scale(z.radius - 1.5));
                    l.teleportTo(to.x, l.getY(), to.z);
                    l.fallDistance = 0;
                    Fx.impact(z.level, to.add(0, 1, 0), 1.2);
                }
            }
            return false;
        });
    }

    // ------------------------------------------------------------------ wounds, weaknesses, regeneration
    /** The Darkness Devil's wounds won't heal. */
    @SubscribeEvent
    public static void unhealing(net.minecraftforge.event.entity.living.LivingHealEvent event) {
        if (event.getEntity().hasEffect(com.csm.hybrids.registry.ModEffects.UNHEALING.get())) {
            event.setCanceled(true);
        }
    }

    /** The Darkness Devil fears fire: it burns twice as badly (as a mob and as a player's form). */
    @SubscribeEvent
    public static void darknessFire(net.minecraftforge.event.entity.living.LivingHurtEvent event) {
        if (event.getSource().is(DamageTypeTags.IS_FIRE) && isDevil(event.getEntity(), HybridType.DARKNESS)) {
            event.setAmount(event.getAmount() * 2f);
        }
    }

    static boolean isDevil(LivingEntity e, HybridType type) {
        if (e instanceof DevilEntity d) {
            return d.devilType() == type;
        }
        if (e instanceof Player p) {
            HybridData d = HybridCapability.get(p);
            return d != null && d.type() == type && d.isTransformed();
        }
        return false;
    }

    /** Standing devil traits that tick: the Eternity Devil keeps knitting back, the Darkness Devil shrinks from light. */
    @SubscribeEvent
    public static void devilTraits(LivingEvent.LivingTickEvent event) {
        LivingEntity e = event.getEntity();
        if (e.tickCount % 20 != 0 || !(e.level() instanceof ServerLevel level)) {
            return;
        }
        if (isDevil(e, HybridType.ETERNITY) && e.getHealth() < e.getMaxHealth()) {
            e.heal(e instanceof Player ? 1f : 3f);
        }
        if (isDevil(e, HybridType.DARKNESS)) {
            int light = level.getBrightness(net.minecraft.world.level.LightLayer.BLOCK,
                    net.minecraft.core.BlockPos.containing(e.getEyePosition()));
            if (light >= 12) {
                e.hurt(e.damageSources().magic(), 2f);
                e.addEffect(new net.minecraft.world.effect.MobEffectInstance(
                        net.minecraft.world.effect.MobEffects.WEAKNESS, 40, 1));
                Fx.smoke(level, e.getEyePosition(), 6, 0.5);
            }
        }
    }

    /**
     * Seeing the future: while the Future Devil's foresight lasts, blows simply miss (it steps aside). The Future
     * Devil as a mob always half-sees them coming, and so, now and then, does a contractor with it in their eye. A
     * Ghost that has gone intangible can't be touched at all.
     */
    @SubscribeEvent(priority = EventPriority.HIGHEST)
    public static void untouchable(LivingAttackEvent event) {
        LivingEntity victim = event.getEntity();
        if (!(victim.level() instanceof ServerLevel level) || event.getSource().is(DamageTypeTags.BYPASSES_INVULNERABILITY)) {
            return;
        }
        CompoundTag tag = victim.getPersistentData();
        if (tag.getLong(ContractMoves.INTANGIBLE_UNTIL) > level.getGameTime()) {
            event.setCanceled(true);
            return;
        }
        Entity attacker = event.getSource().getEntity();
        if (attacker == null || attacker == victim) {
            return;
        }
        boolean foresight = tag.getLong(ContractMoves.FORESIGHT_UNTIL) > level.getGameTime()
                && tag.getInt(ContractMoves.FORESIGHT_CHARGES) > 0;
        boolean instinct = (victim instanceof DevilEntity d && d.devilType() == HybridType.FUTURE
                && level.random.nextFloat() < 0.25f) || futureEye(victim, level);
        if (!foresight && !instinct) {
            return;
        }
        event.setCanceled(true);
        if (foresight) {
            tag.putInt(ContractMoves.FORESIGHT_CHARGES, tag.getInt(ContractMoves.FORESIGHT_CHARGES) - 1);
        }
        if (victim.invulnerableTime > 0) {
            return;
        }
        victim.invulnerableTime = 10;
        Vec3 from = attacker.position().subtract(victim.position());
        Vec3 side = new Vec3(-from.z, 0, from.x);
        if (side.lengthSqr() > 1e-4 && !(victim instanceof DevilEntity d2 && d2.devilType() == HybridType.FUTURE)) {
            side = side.normalize().scale(level.random.nextBoolean() ? 0.9 : -0.9);
            victim.setDeltaMovement(side.x, 0.1, side.z);
            victim.hurtMarked = true;
        }
        Fx.speedLine(level, victim.getBoundingBox().getCenter(), victim.getBoundingBox().getCenter().add(side));
        Fx.stars(level, victim.getEyePosition(), 3, 0.3);
        AbilityUtil.soundAt(level, victim.position(), com.csm.hybrids.registry.ModSounds.FLASH_STEP.get(), 0.6f, 1.6f);
    }

    /** The Future Devil living in a contractor's right eye sometimes shows them the blow coming. */
    private static boolean futureEye(LivingEntity victim, ServerLevel level) {
        if (!(victim instanceof Player p)) {
            return false;
        }
        HybridData d = HybridCapability.get(p);
        return d != null && d.hasContract(com.csm.hybrids.contract.Contract.FUTURE) && level.random.nextFloat() < 0.08f;
    }

    /** The death the Future Devil showed comes true. */
    @SubscribeEvent
    public static void doom(LivingEvent.LivingTickEvent event) {
        LivingEntity e = event.getEntity();
        if (!(e.level() instanceof ServerLevel level)) {
            return;
        }
        CompoundTag tag = e.getPersistentData();
        long at = tag.getLong(ContractMoves.DOOM_AT);
        if (at == 0 || level.getGameTime() < at) {
            return;
        }
        float dmg = tag.getFloat("csm_doom_dmg");
        Entity by = tag.hasUUID(ContractMoves.DOOM_BY) ? level.getEntity(tag.getUUID(ContractMoves.DOOM_BY)) : null;
        tag.remove(ContractMoves.DOOM_AT);
        tag.remove(ContractMoves.DOOM_BY);
        tag.remove("csm_doom_dmg");
        e.invulnerableTime = 0;
        e.hurt(by instanceof LivingEntity l ? AbilityUtil.source(l) : e.damageSources().magic(), dmg);
        Vec3 c = e.getBoundingBox().getCenter();
        AbilityUtil.blood(level, c, 50, 0.4);
        Fx.impact(level, c, 1.2);
    }

    /** The Doll Devil's touch spreads: whoever a doll hurts becomes a doll of the same contractor. */
    @SubscribeEvent
    public static void dollTouch(net.minecraftforge.event.entity.living.LivingHurtEvent event) {
        LivingEntity victim = event.getEntity();
        if (!(victim.level() instanceof ServerLevel level)
                || !(event.getSource().getEntity() instanceof Mob doll)) {
            return;
        }
        CompoundTag tag = doll.getPersistentData();
        if (!tag.getBoolean(com.csm.hybrids.contract.Contracts.DOLL) || !tag.hasUUID(DevilEntity.THRALL_TAG)) {
            return;
        }
        UUID masterId = tag.getUUID(DevilEntity.THRALL_TAG);
        if (level.getEntity(masterId) instanceof LivingEntity master && !isThrallOf(victim, masterId)
                && com.csm.hybrids.contract.Contracts.makeDoll(level, master, victim)) {
            event.setCanceled(true); // it isn't hurt: it is someone else's now
        }
    }

    private static boolean isThrallOf(Entity e, UUID master) {
        CompoundTag t = e.getPersistentData();
        return t.hasUUID(DevilEntity.THRALL_TAG) && t.getUUID(DevilEntity.THRALL_TAG).equals(master);
    }

    private DevilEvents() {
    }
}
