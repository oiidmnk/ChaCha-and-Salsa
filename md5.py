from cryptopals_lib import *

class MD5(object):
	def __init__(self):
		self.buffers = [0x67452301, 0xEFCDAB89, 0x98BADCFE, 0x10325476]

		self.sin_constants = [asint32(int(abs(math.sin(i+1)) * 2**32)) for i in range(64)]

		self.shift_table = [7, 12, 17, 22, 7, 12, 17, 22, 7, 12, 17, 22, 7, 12, 17, 22,
							5,  9, 14, 20, 5,  9, 14, 20, 5,  9, 14, 20, 5,  9, 14, 20,
							4, 11, 16, 23, 4, 11, 16, 23, 4, 11, 16, 23, 4, 11, 16, 23,
							6, 10, 15, 21, 6, 10, 15, 21, 6, 10, 15, 21, 6, 10, 15, 21]

	def _set_message(self, message):
		#Convert to bytes if not already
		byte_message = bytearray(message)

		#Get Length shifted by 8 and limit to 64bit int
		md5_input_length_data = asint64(len(byte_message) << 3)

		#Append 0x80 to the end of the message as a end of message byte
		byte_message.append(0x80)

		#Pad the data to a multable of 64 bytes when the 8 byte md5_input_length_data is added 
		while len(byte_message) % 64 != 56:
			byte_message.append(0x00)

		#Append the length data to the message
		byte_message += int_to_bytes_length(md5_input_length_data, 8, False)

		return byte_message

	def _hash_message_chunk(self, chunk):
		temp_buffers = self.buffers[:]

		for round_itteration in range(16):
			#Do Function F (x & y) | (~x & z)
			temp_value = (temp_buffers[1] & temp_buffers[2]) | (~temp_buffers[1] & temp_buffers[3])

			#Calculate index to opperate on
			chunk_index = round_itteration * 4

			#Add Varables mod 32
			temp_value = asint32(temp_value + temp_buffers[0] + self.sin_constants[round_itteration] + bytes_to_int(chunk[chunk_index:chunk_index+4], False))
			
			#Rotate based of of rotate table and add the second index in the buffer
			temp_value = asint32(temp_buffers[1] + shift_rotate_left(temp_value, self.shift_table[round_itteration]))

			#Swap values in to the new buffer
			temp_buffers = [temp_buffers[3], temp_value, temp_buffers[1], temp_buffers[2]]


		for round_itteration in range(16, 32):
			#Do Function G (x & z) | (y & ~z)
			temp_value = (temp_buffers[1] & temp_buffers[3]) | (temp_buffers[2] & ~temp_buffers[3])

			#Calculate index to opperate on
			chunk_index = (((5 * round_itteration) + 1) % 16) * 4

			#Add Varables mod 32
			temp_value = asint32(temp_value + temp_buffers[0] + self.sin_constants[round_itteration] + bytes_to_int(chunk[chunk_index:chunk_index+4], False))
			
			#Rotate based of of rotate table and add the second index in the buffer
			temp_value = asint32(temp_buffers[1] + shift_rotate_left(temp_value, self.shift_table[round_itteration]))

			#Swap values in to the new buffer
			temp_buffers = [temp_buffers[3], temp_value, temp_buffers[1], temp_buffers[2]]

		for round_itteration in range(32, 48):
			#Do Function H x ^ y ^ z
			temp_value = fixedlen_xor(fixedlen_xor(temp_buffers[1], temp_buffers[2]), temp_buffers[3])

			#Calculate index to opperate on
			chunk_index = (((3 * round_itteration) + 5) % 16) * 4

			#Add Varables mod 32
			temp_value = asint32(temp_value + temp_buffers[0] + self.sin_constants[round_itteration] + bytes_to_int(chunk[chunk_index:chunk_index+4], False))
			
			#Rotate based of of rotate table and add the second index in the buffer
			temp_value = asint32(temp_buffers[1] + shift_rotate_left(temp_value, self.shift_table[round_itteration]))

			#Swap values in to the new buffer
			temp_buffers = [temp_buffers[3], temp_value, temp_buffers[1], temp_buffers[2]]


		for round_itteration in range(48, 64):
			#Do Function I y ^ (x | ~z)
			temp_value = fixedlen_xor(temp_buffers[2], (temp_buffers[1] | ~temp_buffers[3]))

			#Calculate index to opperate on
			chunk_index = ((7 * round_itteration) % 16) * 4

			#Add Varables mod 32
			temp_value = asint32(temp_value + temp_buffers[0] + self.sin_constants[round_itteration] + bytes_to_int(chunk[chunk_index:chunk_index+4], False))
			
			#Rotate based of of rotate table and add the second index in the buffer
			temp_value = asint32(temp_buffers[1] + shift_rotate_left(temp_value, self.shift_table[round_itteration]))

			#Swap values in to the new buffer
			temp_buffers = [temp_buffers[3], temp_value, temp_buffers[1], temp_buffers[2]]

		#Chunks are done with the round
		#Update the internal buffers with the new data
		self.buffers = [asint32(self.buffers[0] + temp_buffers[0]), 
						asint32(self.buffers[1] + temp_buffers[1]),
						asint32(self.buffers[2] + temp_buffers[2]),
						asint32(self.buffers[3] + temp_buffers[3])]


	def hash(self, message):
		#Setup message with padding and length data
		byte_message = self._set_message(message)

		#Opperate on each of the 64 byte chunks
		for chunk in to_blocks(byte_message, 64):
			self._hash_message_chunk(chunk)

		#Convert Intagers to Byte string
		output = b""
		for x in self.buffers:
			output += (x).to_bytes(4, byteorder='little')

		
		return output
		
	def hash_digest(self, message):
		return self.hash(message).hex()

if __name__ == '__main__':
	testmd5 = MD5()
	print(testmd5.hash_digest(b""))
	#d41d8cd98f00b204e9800998ecf8427e

	testmd5 = MD5()
	print(testmd5.hash_digest(b"a"))
	#0cc175b9c0f1b6a831c399e269772661

	testmd5 = MD5()
	print(testmd5.hash_digest(b"c7840924e344f6d3934999be91f1f079c759cfc1d7ebb38655b49415df9a1c67b9345d01c0c0aaacd51357f74e356d75fc7e22322637d54d43331b143e268b297eee06be41abefdd2b78cdc33a7f9372e9f4df44d0c5d3a981c7084b2cc6be181b13251f2151cc03d2b0c6d001c13105dd1d5bd7e3200696545ed7ed9c1dc2662fe34f35b8caffbb0466b129736fa4b0ad18e21297836814561cdeaba49b345b6f5e3717a322485acb01ba9af6fe085052bdd158ab930b80b0c96eb2fd28570e9c81579f304443a8c3e4c4e3c0968444acc65e000730b4399719936c7e141d40b6d721f4fa97254465a9ddf51f1e70ad340ad8cc27671fd8a28bda7ec2ce475ebf1819b448f8804c2a2df277ae613974c889a7dc0bfa42698e29e663e0d5591324221267fc5d3ff101e81afdb4f9fb4a40c025bbab9c5809bd297904e6ca3b8036cc4ead33ea28639803cac1a5a67572bbc7947254d15d8befd44e7125920ba5f6f6e87cf07e75e56ea47f3817ff35de2033652a5c9a797d44b811c6482a345d0201a3064b6dd9e6b86735c16efd34120a3adb3496fc52472175056bef762f76e93bd6e7253f4c2baaddeb7d2aa1ee187909fc842276021ce38c82ad57594eb416f80fa0804437a501b21e9f8643d6120b9c0ab5d7624e1c3354c473446757dd1c722f5703055598d16d2458b77defbab48b87ca205339e4417a4486958d96db"))
	#85bdc64de404bf5ab58e313fd6aa089b
