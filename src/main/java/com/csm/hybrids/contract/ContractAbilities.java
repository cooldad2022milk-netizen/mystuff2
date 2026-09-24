package com.csm.hybrids.contract;

import com.csm.hybrids.ability.Ability;
import com.csm.hybrids.ability.AbilityRun;
import com.csm.hybrids.ability.AbilityUtil;
import com.csm.hybrids.ability.devil.ContractMoves;
import com.csm.hybrids.entity.ContractSummonEntity;
import com.csm.hybrids.entity.ContractSummonEntity.Kind;
import com.csm.hybrids.fx.Fx;
import com.csm.hybrids.hybrid.HybridData;
import com.csm.hybrids.registry.ModSounds;
import net.minecraft.ChatFormatting;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.world.effect.MobEffectInstance;
import net.minecraft.world.effect.MobEffects;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.Mob;
import net.minecraft.world.phys.Vec3;

import java.util.EnumMap;
import java.util.List;
import java.util.Map;

/** The moves each contract puts on the ability wheel. */
public final class ContractAbilities {
    private static final Map<Contract, List<Ability>> CACHE = new EnumMap<>(Contract.class);

    public static synchronized List<Ability> forContract(Contract c) {
        return CACHE.computeIfAbsent(c, ContractAbilities::build);
    }

    private static List<Ability> build(Contract c) {
        return switch (c) {
            case FOX_HEAD -> List.of(new Kon());
            case FOX_PAW -> List.of(new PawSlam(), new PawSwipe());
            case CURSE -> List.of(new CurseNail());
            case FUTURE -> List.of(new FutureSight());
            case GHOST -> List.of(new GhostHand(), new GhostFling());
            case SNAKE -> List.of(new SnakeSwallow(), new SnakeRelease(), new SnakeTail());
            case OCTOPUS -> List.of(new OctopusGrab(), new OctopusInk(), new TentacleLift());
            case DOLL -> List.of(new DollTouch(), new DollCommand());
            case HELL -> List.of(new HellHand());
        };
    }

    private static Vec3 flat(Vec3 v) {
        return new Vec3(v.x, 0, v.z);
    }

    // ================================================================== Fox Devil: the head
    /**
     * "Kon!" - make the fox with your hand, point it, say the word. Only the Fox Devil's head comes: it appears around
     * the prey with its jaws wide open and bites down (swallowing small things whole).
     */
    public static class Kon extends ContractAbility {
        public Kon() {
            super(Contract.FOX_HEAD, "contract_kon");
            timing(18, 140);
            anim("contract_kon", "");
            reach(28);
            flesh(2f);
        }

        @Override
        protected void perform(ServerPlayer player, HybridData data, AbilityRun run) {
            if (run.tick == 5) {
                AbilityUtil.sound(player, SoundEvents.FOX_SCREECH, 1.2f, 0.55f);
            }
            if (run.tick != 6) {
                return;
            }
            LivingEntity t = target(run);
            Vec3 at = t != null ? t.position() : Contracts.aimPoint(player, reach);
            ContractSummonEntity.summon(player.serverLevel(), Kind.FOX_HEAD, player, t, at,
                    flat(at.subtract(player.position())));
        }
    }

    // ================================================================== Fox Devil: the paw
    /** The Fox Devil's paw, covered in eyes, drops out of the sky onto what you point at. */
    public static class PawSlam extends ContractAbility {
        public PawSlam() {
            super(Contract.FOX_PAW, "contract_paw_slam");
            timing(14, 80);
            anim("contract_paw", "");
            reach(24);
            flesh(1f);
        }

        @Override
        protected void perform(ServerPlayer player, HybridData data, AbilityRun run) {
            if (run.tick != 4) {
                return;
            }
            LivingEntity t = target(run);
            Vec3 at = t != null ? t.position() : Contracts.aimPoint(player, reach);
            AbilityUtil.sound(player, SoundEvents.FOX_AGGRO, 1.0f, 0.6f);
            ContractSummonEntity.summon(player.serverLevel(), Kind.FOX_PAW_SLAM, player, t, at,
                    flat(at.subtract(player.position())));
        }
    }

    /** The paw sweeps across in front of you and bats everything aside. */
    public static class PawSwipe extends ContractAbility {
        public PawSwipe() {
            super(Contract.FOX_PAW, "contract_paw_swipe");
            timing(14, 60);
            anim("contract_paw_swipe", "");
            reach(8);
            flesh(1f);
        }

        @Override
        protected void perform(ServerPlayer player, HybridData data, AbilityRun run) {
            if (run.tick != 2) {
                return;
            }
            AbilityUtil.sound(player, SoundEvents.FOX_AGGRO, 1.0f, 0.7f);
            ContractSummonEntity.summon(player.serverLevel(), Kind.FOX_PAW_SWIPE, player, null, player.position(),
                    flat(player.getLookAngle()));
        }
    }

    // ================================================================== Curse Devil
    /**
     * Stab with the nail. Three stabs into the same thing within 30 seconds and a mouth on it counts down to zero:
     * the Curse Devil appears behind it and takes it - and a heart of your lifespan with it.
     */
    public static class CurseNail extends ContractAbility {
        public CurseNail() {
            super(Contract.CURSE, "contract_curse_nail");
            timing(12, 14);
            anim("contract_curse_nail", "");
            reach(4.5);
        }

        @Override
        protected void perform(ServerPlayer player, HybridData data, AbilityRun run) {
            if (run.tick != 5) {
                return;
            }
            ServerLevel level = player.serverLevel();
            Vec3 eye = player.getEyePosition();
            LivingEntity victim = target(run);
            if (victim == null || victim.distanceTo(player) > reach + victim.getBbWidth()) {
                victim = null;
                for (LivingEntity e : AbilityUtil.inCone(player, eye, player.getLookAngle(), 3.6, 45)) {
                    victim = e;
                    break;
                }
            }
            AbilityUtil.sound(player, ModSounds.SPEAR_IMPACT.get(), 0.9f, 1.7f);
            if (victim == null) {
                return;
            }
            AbilityUtil.hurtIgnoringIFrames(player, victim, 5f);
            Vec3 c = victim.getBoundingBox().getCenter();
            AbilityUtil.blood(level, c, 12, 0.2);
            CompoundTag tag = victim.getPersistentData();
            int stacks = tag.getLong(ContractMoves.CURSE_UNTIL) > level.getGameTime() ? tag.getInt(ContractMoves.CURSE_STACKS) : 0;
            stacks++;
            Fx.shards(level, c, 6 * stacks, 0.2);
            if (stacks >= 3) {
                tag.putInt(ContractMoves.CURSE_STACKS, 0);
                tag.putLong(ContractMoves.CURSE_UNTIL, 0);
                Contracts.curseManifest(player, data, victim);
            } else {
                tag.putInt(ContractMoves.CURSE_STACKS, stacks);
                tag.putLong(ContractMoves.CURSE_UNTIL, level.getGameTime() + 600);
                // lips open on the wound and count down
                player.displayClientMessage(Component.translatable("msg.csm.curse_count", 3 - stacks)
                        .withStyle(ChatFormatting.DARK_RED), true);
                AbilityUtil.sound(player, ModSounds.DEVIL_GROWL.get(), 0.5f + stacks * 0.3f, 0.5f);
            }
        }
    }

    // ================================================================== Future Devil
    /**
     * The Future Devil in your right eye shows you the next few seconds: for 15 seconds the next four blows aimed at
     * you miss, and you can see everything that means you harm.
     */
    public static class FutureSight extends ContractAbility {
        public FutureSight() {
            super(Contract.FUTURE, "contract_future_sight");
            timing(16, 600);
            anim("contract_future", "");
        }

        @Override
        protected void perform(ServerPlayer player, HybridData data, AbilityRun run) {
            if (run.tick != 8) {
                return;
            }
            ServerLevel level = player.serverLevel();
            CompoundTag tag = player.getPersistentData();
            tag.putLong(ContractMoves.FORESIGHT_UNTIL, level.getGameTime() + 300);
            tag.putInt(ContractMoves.FORESIGHT_CHARGES, 4);
            AbilityUtil.sound(player, ModSounds.COSMOS_HALLOWEEN.get(), 0.8f, 1.6f);
            Fx.stars(level, player.getEyePosition(), 14, 0.4);
            for (LivingEntity e : AbilityUtil.inRadius(player, player.position(), 24)) {
                if (e instanceof Mob m && m.getTarget() == player) {
                    e.addEffect(AbilityUtil.quiet(new MobEffectInstance(MobEffects.GLOWING, 300, 0)));
                }
            }
            player.displayClientMessage(Component.translatable("msg.csm.future_sight").withStyle(ChatFormatting.GOLD),
                    true);
        }
    }

    // ================================================================== Ghost Devil
    /** The Ghost Devil's invisible right hand closes round a throat, lifts and squeezes. */
    public static class GhostHand extends ContractAbility {
        public GhostHand() {
            super(Contract.GHOST, "contract_ghost_hand");
            timing(20, 180);
            anim("contract_ghost_grab", "");
            reach(18);
        }

        @Override
        protected void perform(ServerPlayer player, HybridData data, AbilityRun run) {
            if (run.tick != 4) {
                return;
            }
            LivingEntity t = target(run);
            if (t == null) {
                player.displayClientMessage(Component.translatable("msg.csm.ghost_nothing").withStyle(ChatFormatting.GRAY),
                        true);
                return;
            }
            Vec3 neck = t.position().add(0, t.getBbHeight() * 0.85, 0);
            ContractSummonEntity.summon(player.serverLevel(), Kind.GHOST_HAND, player, t, neck,
                    flat(t.position().subtract(player.position())));
        }
    }

    /** The invisible hand snatches something up and throws it aside. */
    public static class GhostFling extends ContractAbility {
        public GhostFling() {
            super(Contract.GHOST, "contract_ghost_fling");
            timing(16, 90);
            anim("contract_ghost_fling", "");
            reach(16);
        }

        @Override
        protected void perform(ServerPlayer player, HybridData data, AbilityRun run) {
            if (run.tick != 3) {
                return;
            }
            LivingEntity t = target(run);
            if (t == null) {
                player.displayClientMessage(Component.translatable("msg.csm.ghost_nothing").withStyle(ChatFormatting.GRAY),
                        true);
                return;
            }
            ContractSummonEntity.summon(player.serverLevel(), Kind.GHOST_FLING, player, t, t.position(),
                    flat(t.position().subtract(player.position())));
        }
    }

    // ================================================================== Snake Devil (Sawatari)
    /** A command costs a fingernail. */
    private static final float FINGERNAIL = 1f;

    /** The snake's head comes up under the target, facing the contractor. */
    private static Vec3 snakeFacing(ServerPlayer player, Vec3 at) {
        Vec3 f = flat(player.position().subtract(at));
        return f.lengthSqr() > 1e-4 ? f : flat(player.getLookAngle()).reverse();
    }

    /**
     * "Snake - swallow it." The Snake Devil's head bursts up out of the ground under the prey, its mouth of interlocking
     * hands wide open, and swallows it whole. Anything weak enough is kept in its belly to be let out later; the rest
     * is badly bitten.
     */
    public static class SnakeSwallow extends ContractAbility {
        public SnakeSwallow() {
            super(Contract.SNAKE, "contract_snake_swallow");
            timing(16, 220);
            anim("contract_snake", "");
            reach(24);
            flesh(FINGERNAIL);
        }

        @Override
        protected void perform(ServerPlayer player, HybridData data, AbilityRun run) {
            if (run.tick != 5) {
                return;
            }
            LivingEntity t = target(run);
            Vec3 at = t != null ? t.position() : Contracts.aimPoint(player, reach);
            AbilityUtil.sound(player, ModSounds.DEVIL_GROWL.get(), 1.0f, 1.4f);
            ContractSummonEntity.summon(player.serverLevel(), Kind.SNAKE_SWALLOW, player, t, at, snakeFacing(player, at));
        }
    }

    /**
     * "Release." The snake rises where you point and spits out the last thing it swallowed: whole again, healed, and
     * fighting for you for two minutes. It costs a fingernail and a nosebleed.
     */
    public static class SnakeRelease extends ContractAbility {
        public SnakeRelease() {
            super(Contract.SNAKE, "contract_snake_release");
            timing(16, 300);
            anim("contract_snake_release", "");
            reach(16);
            flesh(FINGERNAIL + 2f);
        }

        @Override
        public String checkUse(ServerPlayer player, HybridData data) {
            String fail = super.checkUse(player, data);
            if (fail != null) {
                return fail;
            }
            return Contracts.bellyCount(player) == 0 ? "msg.csm.snake_empty" : null;
        }

        @Override
        protected void perform(ServerPlayer player, HybridData data, AbilityRun run) {
            if (run.tick == 2) {
                AbilityUtil.blood(player.serverLevel(), player.getEyePosition().add(player.getLookAngle().scale(0.2))
                        .add(0, -0.15, 0), 8, 0.05); // the nosebleed
            }
            if (run.tick != 5) {
                return;
            }
            LivingEntity t = target(run);
            Vec3 at = Contracts.aimPoint(player, reach);
            if (t != null && t.distanceTo(player) > 4) {
                at = t.position().add(flat(player.position().subtract(t.position())).normalize().scale(3.0));
            }
            ContractSummonEntity.summon(player.serverLevel(), Kind.SNAKE_RELEASE, player, t, at, snakeFacing(player, at));
        }
    }

    /** The Snake Devil's thick tail bursts out of the ground beside you and swats everything in front of you away. */
    public static class SnakeTail extends ContractAbility {
        public SnakeTail() {
            super(Contract.SNAKE, "contract_snake_tail");
            timing(14, 90);
            anim("contract_snake_tail", "");
            reach(8);
            flesh(FINGERNAIL);
        }

        @Override
        protected void perform(ServerPlayer player, HybridData data, AbilityRun run) {
            if (run.tick != 2) {
                return;
            }
            Vec3 fwd = flat(player.getLookAngle()).normalize();
            Vec3 right = new Vec3(-fwd.z, 0, fwd.x);
            Vec3 at = player.position().add(right.scale(2.2)).add(fwd.scale(0.5));
            AbilityUtil.sound(player, ModSounds.DEVIL_GROWL.get(), 1.0f, 1.2f);
            ContractSummonEntity.summon(player.serverLevel(), Kind.SNAKE_TAIL, player, null, at, fwd);
        }
    }

    // ================================================================== Octopus Devil (Yoshida)
    /**
     * Cross your index and middle fingers: the Octopus Devil's tentacles come up out of clouds of ink round the target,
     * coil round it (and whatever stands next to it), lift, squeeze and smash it down.
     */
    public static class OctopusGrab extends ContractAbility {
        public OctopusGrab() {
            super(Contract.OCTOPUS, "contract_octopus");
            timing(16, 180);
            anim("contract_octopus", "");
            reach(24);
            hunger(8f);
        }

        @Override
        protected void perform(ServerPlayer player, HybridData data, AbilityRun run) {
            if (run.tick != 5) {
                return;
            }
            LivingEntity t = target(run);
            Vec3 at = t != null ? t.position() : Contracts.aimPoint(player, reach);
            AbilityUtil.sound(player, ModSounds.SHARK_DIVE.get(), 1.2f, 0.6f);
            ContractSummonEntity.summon(player.serverLevel(), Kind.OCTOPUS_GRAB, player, t, at,
                    flat(at.subtract(player.position())));
        }
    }

    /** The Octopus Devil sprays a cloud of ink round you: everything in it is blind and loses sight of you. */
    public static class OctopusInk extends ContractAbility {
        public OctopusInk() {
            super(Contract.OCTOPUS, "contract_octopus_ink");
            timing(12, 320);
            anim("contract_octopus_ink", "");
            hunger(4f);
        }

        @Override
        protected void perform(ServerPlayer player, HybridData data, AbilityRun run) {
            if (run.tick != 4) {
                return;
            }
            ServerLevel level = player.serverLevel();
            Vec3 c = player.position().add(0, 1.0, 0);
            Fx.ink(level, c, 90, 2.8);
            Fx.ink(level, c.add(0, 1.2, 0), 40, 3.5);
            AbilityUtil.sound(player, ModSounds.SHARK_DIVE.get(), 1.4f, 0.5f);
            for (LivingEntity e : AbilityUtil.inRadius(player, c, 8)) {
                e.addEffect(AbilityUtil.quiet(new MobEffectInstance(MobEffects.BLINDNESS, 120, 0)));
                e.addEffect(AbilityUtil.quiet(new MobEffectInstance(MobEffects.MOVEMENT_SLOWDOWN, 60, 1)));
                if (e instanceof Mob m && m.getTarget() == player) {
                    m.setTarget(null);
                }
            }
            player.addEffect(AbilityUtil.quiet(new MobEffectInstance(MobEffects.INVISIBILITY, 70, 0)));
            player.addEffect(AbilityUtil.quiet(new MobEffectInstance(MobEffects.MOVEMENT_SPEED, 70, 1)));
        }
    }

    /** A tentacle comes up out of a puddle of ink under your feet and flings you the way you're looking. */
    public static class TentacleLift extends ContractAbility {
        public TentacleLift() {
            super(Contract.OCTOPUS, "contract_octopus_lift");
            timing(40, 120);
            anim("contract_octopus_lift", "");
            hunger(3f);
        }

        @Override
        protected void perform(ServerPlayer player, HybridData data, AbilityRun run) {
            player.fallDistance = 0;
            if (run.tick == 1) {
                ContractSummonEntity.summon(player.serverLevel(), Kind.OCTOPUS_LIFT, player, null, player.position(),
                        flat(player.getLookAngle()));
                Fx.ink(player.serverLevel(), player.position().add(0, 0.2, 0), 20, 0.8);
            }
            if (run.tick == 6) {
                Vec3 look = player.getLookAngle();
                Vec3 f = flat(look).lengthSqr() > 1e-4 ? flat(look).normalize() : Vec3.ZERO;
                player.setDeltaMovement(f.x * 1.5, 0.95 + Math.max(0, look.y) * 0.6, f.z * 1.5);
                player.hurtMarked = true;
                AbilityUtil.sound(player, ModSounds.DEVIL_GUST.get(), 1.2f, 1.1f);
            }
        }
    }

    // ================================================================== Doll Devil (Santa Claus)
    /**
     * Touch someone and they are your doll: they obey you, one of their arms is a blade now, and there is no turning
     * them back. Anyone a doll hurts becomes a doll too. It does nothing to devils, hybrids or fiends.
     */
    public static class DollTouch extends ContractAbility {
        public DollTouch() {
            super(Contract.DOLL, "contract_doll_touch");
            timing(10, 100);
            anim("contract_doll_touch", "");
            reach(4.5);
        }

        @Override
        protected void perform(ServerPlayer player, HybridData data, AbilityRun run) {
            if (run.tick != 4) {
                return;
            }
            LivingEntity t = target(run);
            if (t == null || t.distanceTo(player) > reach + t.getBbWidth()) {
                player.displayClientMessage(Component.translatable("msg.csm.doll_nothing").withStyle(ChatFormatting.GRAY),
                        true);
                return;
            }
            ServerLevel level = player.serverLevel();
            if (!Contracts.dollable(t)) {
                player.displayClientMessage(Component.translatable("msg.csm.doll_immune", t.getDisplayName())
                        .withStyle(ChatFormatting.GRAY), true);
                return;
            }
            if (!Contracts.makeDoll(level, player, t)) {
                player.displayClientMessage(Component.translatable("msg.csm.doll_max", Contracts.MAX_DOLLS)
                        .withStyle(ChatFormatting.GRAY), true);
                return;
            }
            player.displayClientMessage(Component.translatable("msg.csm.doll_made", t.getDisplayName(),
                    Contracts.dollCount(level, player)).withStyle(ChatFormatting.RED), true);
        }
    }

    /** Every doll you have turns on what you point at (or, pointing at nothing, comes back to you). */
    public static class DollCommand extends ContractAbility {
        public DollCommand() {
            super(Contract.DOLL, "contract_doll_command");
            timing(12, 60);
            anim("contract_doll_command", "");
            reach(48);
        }

        @Override
        protected void perform(ServerPlayer player, HybridData data, AbilityRun run) {
            if (run.tick != 4) {
                return;
            }
            ServerLevel level = player.serverLevel();
            LivingEntity t = target(run);
            if (t != null && t.getPersistentData().getBoolean(Contracts.DOLL)) {
                t = null; // pointing at one of your own dolls: call them in
            }
            if (t != null) {
                player.setLastHurtMob(t); // thralls go for what their master last hurt
            }
            int n = 0;
            for (Mob m : level.getEntitiesOfClass(Mob.class, player.getBoundingBox().inflate(Contracts.DOLL_RANGE),
                    m -> m.getPersistentData().getBoolean(Contracts.DOLL)
                            && m.getPersistentData().hasUUID(com.csm.hybrids.entity.devil.DevilEntity.THRALL_TAG)
                            && m.getPersistentData().getUUID(com.csm.hybrids.entity.devil.DevilEntity.THRALL_TAG)
                            .equals(player.getUUID()))) {
                m.addEffect(AbilityUtil.quiet(new MobEffectInstance(MobEffects.MOVEMENT_SPEED, 120, 1)));
                if (t != null) {
                    m.setTarget(t);
                } else {
                    m.setTarget(null);
                    m.getNavigation().moveTo(player, 1.3);
                }
                Fx.stars(level, m.getEyePosition().add(0, 0.4, 0), 2, 0.15);
                n++;
            }
            AbilityUtil.sound(player, ModSounds.CONTROL_DOMINATE.get(), 0.8f, 1.5f);
            player.displayClientMessage(Component.translatable(t != null ? "msg.csm.doll_attack" : "msg.csm.doll_recall",
                    n).withStyle(ChatFormatting.RED), true);
        }
    }

    // ================================================================== Hell Devil (Santa Claus)
    /**
     * The Hell Devil's giant six-fingered hand comes up out of the ground where you point, closes on everything there
     * and drags it down to Hell. The price is three lives from around you, taken first: your dolls if you have any,
     * then any other creature (never a person). With fewer than three about, Hell doesn't answer.
     */
    public static class HellHand extends ContractAbility {
        public HellHand() {
            super(Contract.HELL, "contract_hell");
            timing(24, 3600);
            anim("contract_hell", "");
            reach(32);
        }

        @Override
        public String checkUse(ServerPlayer player, HybridData data) {
            String fail = super.checkUse(player, data);
            if (fail != null) {
                return fail;
            }
            return Contracts.hellOfferings(player).size() < Contracts.HELL_PRICE ? "msg.csm.hell_price" : null;
        }

        @Override
        protected void perform(ServerPlayer player, HybridData data, AbilityRun run) {
            ServerLevel level = player.serverLevel();
            if (run.tick == 4) {
                // the price first: a single finger comes for each of them
                for (LivingEntity e : Contracts.hellOfferings(player)) {
                    Vec3 c = e.getBoundingBox().getCenter();
                    Fx.fireBurst(level, c, 16, 0.2);
                    Fx.smoke(level, c, 10, 0.3);
                    e.invulnerableTime = 0;
                    e.hurt(level.damageSources().magic(), Float.MAX_VALUE);
                    if (e.isAlive()) {
                        e.kill();
                    }
                }
                AbilityUtil.sound(player, ModSounds.DEVIL_ROAR.get(), 1.4f, 0.4f);
            }
            if (run.tick != 9) {
                return;
            }
            LivingEntity t = target(run);
            Vec3 at = t != null ? t.position() : Contracts.aimPoint(player, reach);
            ContractSummonEntity.summon(level, Kind.HELL_HAND, player, t, at, flat(at.subtract(player.position())));
        }
    }

    private ContractAbilities() {
    }
}
