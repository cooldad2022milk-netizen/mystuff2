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

    private ContractAbilities() {
    }
}
