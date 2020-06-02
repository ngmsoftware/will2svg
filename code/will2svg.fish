# Defined in - @ line 1
function will2svg --description 'konvertiert alle *.wills zu svgs'
	for i in *.will
		set -l i0 (pwd)
		set -l d (mktemp -d)
		cp $i $d
		cd $d
		will_reader.py (basename -s '.will' "$i")
		for j in *.svg
			mv $j alt_{$j}
			cairosvg alt_{$j} -f svg -o $j
			svgtoipe $j
			rm alt_{$j}
			mv *.svg *.ipe $i0
		end
		cd $i0
		rm $d/$i
		rmdir $d
	end
end

# sudo apt-get install cairosvg	svgtoipe
