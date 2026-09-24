package com.csm.hybrids.registry;

import com.csm.hybrids.CsmMod;
import net.minecraft.sounds.SoundEvent;
import net.minecraftforge.registries.DeferredRegister;
import net.minecraftforge.registries.ForgeRegistries;
import net.minecraftforge.registries.RegistryObject;

public final class ModSounds {
    public static final DeferredRegister<SoundEvent> SOUNDS = DeferredRegister.create(ForgeRegistries.SOUND_EVENTS, CsmMod.MODID);

    public static final RegistryObject<SoundEvent> CORD_PULL = reg("chainsaw.cord_pull");
    public static final RegistryObject<SoundEvent> CHAINSAW_START = reg("chainsaw.start");
    public static final RegistryObject<SoundEvent> CHAINSAW_SPUTTER = reg("chainsaw.sputter");
    public static final RegistryObject<SoundEvent> CHAINSAW_IDLE = reg("chainsaw.idle");
    public static final RegistryObject<SoundEvent> CHAINSAW_REV = reg("chainsaw.rev");
    public static final RegistryObject<SoundEvent> CHAINSAW_CUT = reg("chainsaw.cut");
    public static final RegistryObject<SoundEvent> CHAIN_THROW = reg("chainsaw.chain_throw");
    public static final RegistryObject<SoundEvent> CHAIN_HIT = reg("chainsaw.chain_hit");
    public static final RegistryObject<SoundEvent> ARROW_PULL = reg("crossbow.arrow_pull");
    public static final RegistryObject<SoundEvent> CROSSBOW_FIRE = reg("crossbow.fire");
    public static final RegistryObject<SoundEvent> CROSSBOW_CHARGE = reg("crossbow.charge");
    public static final RegistryObject<SoundEvent> CROSSBOW_PIERCE = reg("crossbow.pierce");
    public static final RegistryObject<SoundEvent> FLASH_STEP = reg("crossbow.flash_step");
    public static final RegistryObject<SoundEvent> MOLAR_CLICK = reg("flamethrower.molar");
    public static final RegistryObject<SoundEvent> FLAME_IGNITE = reg("flamethrower.ignite");
    public static final RegistryObject<SoundEvent> FLAME_STREAM = reg("flamethrower.stream");
    public static final RegistryObject<SoundEvent> FLAME_BURST = reg("flamethrower.burst");
    public static final RegistryObject<SoundEvent> WHIP_SNAP = reg("whip.snap");
    public static final RegistryObject<SoundEvent> WHIP_CRACK = reg("whip.crack");
    public static final RegistryObject<SoundEvent> WHIP_LASH = reg("whip.lash");
    public static final RegistryObject<SoundEvent> BOMB_PIN = reg("bomb.pin");
    public static final RegistryObject<SoundEvent> BOMB_BLAST = reg("bomb.blast");
    public static final RegistryObject<SoundEvent> BOMB_EXPLOSION = reg("bomb.explosion");
    public static final RegistryObject<SoundEvent> BOMB_FUSE = reg("bomb.fuse");
    public static final RegistryObject<SoundEvent> SPEAR_PULL = reg("spear.pull");
    public static final RegistryObject<SoundEvent> SPEAR_THROW = reg("spear.throw");
    public static final RegistryObject<SoundEvent> SPEAR_IMPACT = reg("spear.impact");
    public static final RegistryObject<SoundEvent> SPEAR_ERUPT = reg("spear.erupt");
    public static final RegistryObject<SoundEvent> KATANA_DRAW = reg("katana.draw");
    public static final RegistryObject<SoundEvent> KATANA_SLASH = reg("katana.slash");
    public static final RegistryObject<SoundEvent> KATANA_IAI = reg("katana.iai");
    public static final RegistryObject<SoundEvent> KATANA_SHEATHE = reg("katana.sheathe");
    public static final RegistryObject<SoundEvent> LONGSWORD_DRAW = reg("longsword.draw");
    public static final RegistryObject<SoundEvent> LONGSWORD_CLANG = reg("longsword.clang");
    public static final RegistryObject<SoundEvent> LONGSWORD_CLEAVE = reg("longsword.cleave");
    public static final RegistryObject<SoundEvent> BLOOD_FORM = reg("blood.form");
    public static final RegistryObject<SoundEvent> BLOOD_SLAM = reg("blood.slam");
    public static final RegistryObject<SoundEvent> BLOOD_RAIN = reg("blood.rain");
    public static final RegistryObject<SoundEvent> SHARK_DIVE = reg("shark.dive");
    public static final RegistryObject<SoundEvent> SHARK_BITE = reg("shark.bite");
    public static final RegistryObject<SoundEvent> VIOLENCE_MASK = reg("violence.mask");
    public static final RegistryObject<SoundEvent> VIOLENCE_PUNCH = reg("violence.punch");
    public static final RegistryObject<SoundEvent> COSMOS_HALLOWEEN = reg("cosmos.halloween");
    public static final RegistryObject<SoundEvent> COSMOS_VOID = reg("cosmos.void");
    public static final RegistryObject<SoundEvent> GUN_SHOT = reg("gun.shot");
    public static final RegistryObject<SoundEvent> GUN_CANNON = reg("gun.cannon");
    public static final RegistryObject<SoundEvent> GUN_COCK = reg("gun.cock");
    public static final RegistryObject<SoundEvent> FIEND_POSSESS = reg("fiend.possess");
    public static final RegistryObject<SoundEvent> CONTROL_BANG = reg("control.bang");
    public static final RegistryObject<SoundEvent> CONTROL_CRUSH = reg("control.crush");
    public static final RegistryObject<SoundEvent> CONTROL_CHAIN = reg("control.chain");
    public static final RegistryObject<SoundEvent> CONTROL_DOMINATE = reg("control.dominate");
    public static final RegistryObject<SoundEvent> DEVIL_ROAR = reg("devil.roar");
    public static final RegistryObject<SoundEvent> DEVIL_GROWL = reg("devil.growl");
    public static final RegistryObject<SoundEvent> DEVIL_SCREECH = reg("devil.screech");
    public static final RegistryObject<SoundEvent> DEVIL_DEATH = reg("devil.death");
    public static final RegistryObject<SoundEvent> DEVIL_FLAP = reg("devil.flap");
    public static final RegistryObject<SoundEvent> DEVIL_BITE = reg("devil.bite");
    public static final RegistryObject<SoundEvent> DEVIL_SLAM = reg("devil.slam");
    public static final RegistryObject<SoundEvent> DEVIL_GUST = reg("devil.gust");
    public static final RegistryObject<SoundEvent> HEART_RIP = reg("heart.rip");
    public static final RegistryObject<SoundEvent> HEART_BEAT = reg("heart.beat");
    public static final RegistryObject<SoundEvent> BLOOD_DRINK = reg("blood.drink");
    public static final RegistryObject<SoundEvent> TRANSFORM = reg("hybrid.transform");
    public static final RegistryObject<SoundEvent> REVERT = reg("hybrid.revert");

    private static RegistryObject<SoundEvent> reg(String name) {
        return SOUNDS.register(name, () -> SoundEvent.createVariableRangeEvent(CsmMod.id(name)));
    }

    private ModSounds() {
    }
}
