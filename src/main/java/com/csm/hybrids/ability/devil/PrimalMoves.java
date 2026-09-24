package com.csm.hybrids.ability.devil;

import com.csm.hybrids.ability.Ability;
import com.csm.hybrids.ability.AbilityRun;
import com.csm.hybrids.ability.AbilityUtil;
import com.csm.hybrids.devil.DevilEvents;
import com.csm.hybrids.entity.devil.DevilEntity;
import com.csm.hybrids.fx.Fx;
import com.csm.hybrids.hybrid.HybridType;
import com.csm.hybrids.registry.ModEffects;
import com.csm.hybrids.registry.ModSounds;
import net.minecraft.ChatFormatting;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.effect.MobEffectInstance;
import net.minecraft.world.effect.MobEffects;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.ClipContext;
import net.minecraft.world.phys.BlockHitResult;
import net.minecraft.world.phys.HitResult;
import net.minecraft.world.phys.Vec3;

import java.util.List;

/** The big threats: the Eternity Devil and the Darkness Devil. */
public final class PrimalMoves {

    public static List<Ability> eternity() {
        return List.of(new InfiniteFloor(), new Tide(), new Swallow(), new Endless());
    }

    public static List<Ability> darkness() {
        return List.of(new Severance(), new HellsDarkness(), new UnseenCut(), new Rake());
    }

    // ================================================================== Eternity Devil
    /**
     * The Infinite Floor: everything around it is trapped in a loop for 20 seconds. Walk out of the ring and you walk
     * back in on the far side. The clocks all say 8:18.
     */
    public static class InfiniteFloor extends DevilAbility {
        public InfiniteFloor() {
            super(HybridType.ETERNITY, "eternity_loop");
            timing(40, 900);
            cost(25);
            anim("", "loop");
            ai(0, 18, 10);
            blind();
        }

        @Override
        public void perform(LivingEntity user, AbilityRun run) {
            ServerLevel level = level(user);
            if (run.tick == 6) {
                AbilityUtil.sound(user, ModSounds.COSMOS_VOID.get(), 1.6f, 0.6f);
            }
            if (run.tick != 20) {
                return;
            }
            double r = 14;
            List<LivingEntity> caught = AbilityUtil.inRadius(user, user.position(), r);
            DevilEvents.loopZone(level, user, user.position(), r, 400, caught);
            for (LivingEntity e : caught) {
                if (e instanceof Player p) {
                    p.displayClientMessage(Component.translatable("msg.csm.eternity_loop").withStyle(ChatFormatting.RED),
                            true);
                }
            }
            Fx.shockwave(level, user.position(), r, Fx.BLOOD_RING);
        }
    }

    /** A tide of arms and heads surges out of it and over whatever is in front of it. */
    public static class Tide extends DevilAbility {
        public Tide() {
            super(HybridType.ETERNITY, "eternity_tide");
            timing(28, 90);
            cost(10);
            anim("", "tide");
            ai(2, 12, 12);
        }

        @Override
        public void perform(LivingEntity user, AbilityRun run) {
            if (run.tick != 12) {
                return;
            }
            ServerLevel level = level(user);
            Vec3 aim = AbilityUtil.aim(user);
            Vec3 from = user.position().add(0, user.getBbHeight() * 0.4, 0);
            AbilityUtil.sound(user, ModSounds.BLOOD_FORM.get(), 1.6f, 0.6f);
            for (LivingEntity e : coneTargets(user, run, from, aim, 12, 40)) {
                AbilityUtil.hurtIgnoringIFrames(user, e, 12f);
                e.addEffect(AbilityUtil.quiet(new MobEffectInstance(MobEffects.MOVEMENT_SLOWDOWN, 60, 3)));
                AbilityUtil.push(e, user.position(), 1.0, 0.3);
                AbilityUtil.blood(level, e.getBoundingBox().getCenter(), 20, 0.3);
            }
            for (int k = 1; k <= 6; k++) {
                Vec3 p = from.add(aim.multiply(1, 0, 1).normalize().scale(k * 1.9));
                Fx.gore(level, p, 2);
                Fx.impact(level, p, 1.0);
            }
        }
    }

    /** Its mouths close over whatever is close. */
    public static class Swallow extends DevilAbility {
        public Swallow() {
            super(HybridType.ETERNITY, "eternity_swallow");
            timing(24, 100);
            cost(8);
            anim("", "swallow");
            ai(0, 4, 12);
        }

        @Override
        public void perform(LivingEntity user, AbilityRun run) {
            if (run.tick != 10) {
                return;
            }
            ServerLevel level = level(user);
            AbilityUtil.sound(user, ModSounds.DEVIL_BITE.get(), 1.6f, 0.5f);
            for (LivingEntity e : coneTargets(user, run, user.getEyePosition(), AbilityUtil.aim(user),
                    3.5 + user.getBbWidth() * 0.5, 70)) {
                AbilityUtil.hurtIgnoringIFrames(user, e, 18f);
                AbilityUtil.blood(level, e.getBoundingBox().getCenter(), 50, 0.4);
                user.heal(AbilityUtil.dmg(user, 10f));
                break;
            }
        }
    }

    /** It can't be killed the ordinary way: it just keeps knitting back together. */
    public static class Endless extends DevilAbility {
        public Endless() {
            super(HybridType.ETERNITY, "eternity_endless");
            timing(40, 400);
            cost(15);
            anim("", "regen");
            ai(0, 40, 20);
            blind();
        }

        @Override
        public boolean aiReady(DevilEntity mob, LivingEntity target) {
            return mob.getHealth() < mob.getMaxHealth() * 0.5f;
        }

        @Override
        public void perform(LivingEntity user, AbilityRun run) {
            if (run.tick % 4 == 0) {
                user.heal(user.getMaxHealth() * 0.03f);
                AbilityUtil.blood(level(user), user.getBoundingBox().getCenter(), 6, 0.6);
            }
        }
    }

    // ================================================================== Darkness Devil
    /** With one sweep of its hand, everyone around it loses their arms. */
    public static class Severance extends DevilAbility {
        public Severance() {
            super(HybridType.DARKNESS, "darkness_sever");
            timing(30, 300);
            cost(25);
            anim("", "sever");
            ai(0, 22, 8);
            blind();
        }

        @Override
        public void perform(LivingEntity user, AbilityRun run) {
            ServerLevel level = level(user);
            if (run.tick == 8) {
                AbilityUtil.sound(user, ModSounds.DEVIL_GUST.get(), 1.0f, 0.4f);
            }
            if (run.tick != 15) {
                return;
            }
            AbilityUtil.sound(user, ModSounds.KATANA_IAI.get(), 1.8f, 0.5f);
            for (LivingEntity e : AbilityUtil.inRadius(user, user.position(), 22)) {
                AbilityUtil.hurtIgnoringIFrames(user, e, 18f);
                e.addEffect(AbilityUtil.quiet(new MobEffectInstance(ModEffects.SEVERED.get(), 200, 0)));
                for (InteractionHand hand : InteractionHand.values()) {
                    ItemStack held = e.getItemInHand(hand);
                    if (!held.isEmpty()) {
                        e.spawnAtLocation(held.copy(), 1.0f);
                        e.setItemInHand(hand, ItemStack.EMPTY);
                    }
                }
                Vec3 sh = e.getEyePosition().add(0, -0.45, 0);
                Vec3 side = AbilityUtil.right(e).scale(e.getBbWidth() * 0.6);
                Fx.bloodSpray(level, sh.add(side), side.normalize(), 20, 0.5);
                Fx.bloodSpray(level, sh.subtract(side), side.normalize().scale(-1), 20, 0.5);
                if (e instanceof Player p) {
                    p.displayClientMessage(Component.translatable("msg.csm.severed").withStyle(ChatFormatting.DARK_RED),
                            true);
                }
            }
        }
    }

    /** The world goes dark all round it: nothing can see, and it can. */
    public static class HellsDarkness extends DevilAbility {
        public HellsDarkness() {
            super(HybridType.DARKNESS, "darkness_hell");
            timing(40, 600);
            cost(30);
            anim("", "hell");
            ai(0, 30, 6);
            blind();
        }

        @Override
        public void perform(LivingEntity user, AbilityRun run) {
            ServerLevel level = level(user);
            if (run.tick == 10) {
                AbilityUtil.sound(user, ModSounds.COSMOS_VOID.get(), 2.0f, 0.4f);
            }
            if (run.tick >= 14 && run.tick <= 36 && run.tick % 4 == 0) {
                Fx.smoke(level, user.position().add(0, 1, 0), 20, 4.0 + run.tick * 0.2);
            }
            if (run.tick != 20) {
                return;
            }
            for (LivingEntity e : AbilityUtil.inRadius(user, user.position(), 30)) {
                e.addEffect(AbilityUtil.quiet(new MobEffectInstance(MobEffects.DARKNESS, 240, 0)));
                e.addEffect(AbilityUtil.quiet(new MobEffectInstance(MobEffects.BLINDNESS, 140, 0)));
                e.addEffect(AbilityUtil.quiet(new MobEffectInstance(MobEffects.MOVEMENT_SLOWDOWN, 140, 1)));
            }
            user.addEffect(AbilityUtil.quiet(new MobEffectInstance(MobEffects.DAMAGE_RESISTANCE, 200, 1)));
            Fx.shockwave(level, user.position(), 30, Fx.STEEL_RING);
        }
    }

    /** An unseen force splits everything along a line; the wounds won't close. */
    public static class UnseenCut extends DevilAbility {
        public UnseenCut() {
            super(HybridType.DARKNESS, "darkness_cut");
            timing(20, 80);
            cost(10);
            anim("", "cut");
            ai(3, 30, 12);
            reach(36);
        }

        @Override
        public void perform(LivingEntity user, AbilityRun run) {
            if (run.tick != 9) {
                return;
            }
            ServerLevel level = level(user);
            Vec3 from = user.getEyePosition();
            LivingEntity t = target(run);
            Vec3 dir = t != null ? t.getBoundingBox().getCenter().subtract(from).normalize() : AbilityUtil.aim(user);
            Vec3 end = from.add(dir.scale(32));
            BlockHitResult block = level.clip(new ClipContext(from, end, ClipContext.Block.COLLIDER, ClipContext.Fluid.NONE,
                    user));
            Vec3 limit = block.getType() == HitResult.Type.MISS ? end : block.getLocation();
            AbilityUtil.sound(user, ModSounds.KATANA_SLASH.get(), 1.6f, 0.5f);
            for (LivingEntity e : AbilityUtil.alongLine(user, from, limit, 0.7)) {
                AbilityUtil.hurtIgnoringIFrames(user, e, 20f);
                e.addEffect(AbilityUtil.quiet(new MobEffectInstance(ModEffects.UNHEALING.get(), 200, 0)));
                AbilityUtil.blood(level, e.getBoundingBox().getCenter(), 40, 0.35);
                Fx.slash(level, e.getBoundingBox().getCenter(), dir.cross(new Vec3(0, 1, 0)).add(0, 0.6, 0), 1.6);
            }
            for (int k = 1; k <= 8; k++) {
                Fx.slash(level, from.add(limit.subtract(from).scale(k / 8.0)), dir.cross(new Vec3(0, 1, 0)).add(0, 0.6,
                        0), 1.2);
            }
        }
    }

    /** Both clawed hands tear down. */
    public static class Rake extends DevilAbility {
        public Rake() {
            super(HybridType.DARKNESS, "darkness_rake");
            timing(20, 40);
            cost(4);
            anim("", "rake");
            ai(0, 5, 14);
        }

        @Override
        public void perform(LivingEntity user, AbilityRun run) {
            if (run.tick != 9) {
                return;
            }
            ServerLevel level = level(user);
            AbilityUtil.sound(user, ModSounds.WHIP_CRACK.get(), 1.2f, 0.5f);
            for (LivingEntity e : coneTargets(user, run, user.getEyePosition().add(0, -1.5, 0), AbilityUtil.aim(user),
                    5.5 + user.getBbWidth() * 0.5, 70)) {
                AbilityUtil.hurtIgnoringIFrames(user, e, 16f);
                AbilityUtil.blood(level, e.getBoundingBox().getCenter(), 30, 0.3);
                AbilityUtil.push(e, user.position(), 0.8, 0.2);
            }
        }
    }

    private PrimalMoves() {
    }
}
