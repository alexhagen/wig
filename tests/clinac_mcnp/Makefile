all: write read

clean:
	rm -f runt* clinac_no_target_h2_p.out clinac_no_target_h2_n.out clinac_no_target_h2_photo.out clinac_no_target_h2_pol.out

write: clinac_no_target_h2_p.inp
	@make clean
	@PoliMi_205 inp=clinac_no_target_h2_p.inp outp=clinac_no_target_h2_p.out

read: clinac_no_target_h2_n.inp clinac_no_target_h2_photo.out
	@PoliMi_205 inp=clinac_no_target_h2_n.inp outp=clinac_no_target_h2_n.out
