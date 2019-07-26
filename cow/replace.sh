sed -e "s/&amp;/\&/g" -e "s/&apos;/'/g" -e 's/&gt;/>/g' -e 's/&lt;/</g' -e 's/&quot;/"/g' -i'.orig' $1
